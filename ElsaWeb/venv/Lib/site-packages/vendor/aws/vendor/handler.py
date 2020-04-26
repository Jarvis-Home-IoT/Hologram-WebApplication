"""
Vendor AWS Serverless Application.

This AWS Lambda function builds python wheels inside the lambda environment.
These wheels can then be extracted for use in your own lambda functions.
"""
import contextlib
import functools
import json
import logging
import os
import os.path
import re
import shutil
import string
import subprocess
import sys
import tempfile
import traceback

import boto3


# Required config
BUCKET = os.environ['BUCKET']
BUILD_PROXY_AMI = os.environ['BUILD_PROXY_AMI']
BUILD_PROXY_PROFILE = os.environ['BUILD_PROXY_PROFILE']
# Optional config
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# Constants
BUILD_STARTED_MSG = 'Build under way. Once complete, download wheels from {bucket_url}.'
SERVER_ERROR_MSG = '''Something went wrong. Maybe the traceback will help?
Please include it in any issue you raise.

'''
PROXY_PARAM_RE = re.compile(r'\{(?P<key>\w+)\+\}')


logging.basicConfig(level=LOG_LEVEL)

log = logging.getLogger('vendor')


class APIError(Exception):
    """APIError signals an error response for apiproxy()."""

    def __init__(self, status_code, message):
        """
        Create new API Error instance.

        :param int status_code: HTTP Error Code
        :param str message: Error message
        """
        self.status_code = status_code
        self.message = message
        super(APIError, self).__init__(status_code, message)


def _api_response(code, obj):
    return {
        'statusCode': code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(obj),
    }


def apiproxy(function):
    """Make API Gateway Lambda Proxy Integration even friendlier."""
    @functools.wraps(function)
    def proxy(event, context):
        args = []
        kwargs = {}
        match = PROXY_PARAM_RE.search(event['resource'])
        if match:
            ppath = event['pathParameters'].pop(match.group('key'))
            args.extend(ppath.split('/'))

        if event['body']:
            kwargs.update(json.loads(event['body']))
        if event['queryStringParameters']:
            kwargs.update(event['queryStringParameters'])
        if event['pathParameters']:
            kwargs.update(event['pathParameters'])

        try:
            result = function(*args, **kwargs)
        except APIError as err:
            return _api_response(err.status_code, {'message': err.message})
        except Exception:
            log.exception('Error executing %s', function)
            return _api_response(500, {'message': SERVER_ERROR_MSG + traceback.format_exc()})

        return _api_response(200, result)

    return proxy


@apiproxy
def vend(requirements, rebuild=False, minimal=False, bucketname=BUCKET):
    """Vend takes a package name and builds python wheels for it and its dependencies."""
    keys = clone_packages(requirements, bucketname, overwrite=rebuild)
    for key in keys:
        fname = key.rsplit('/', 1)[-1]
        # We assume successful parse as it happened in clone_packages already.
        pi = PackageInfo.parse(fname)
        if pi.is_src():
            # TODO: Check for wheel, only overwrite if rebuild==True.
            build_wheel(key, sys.version_info, bucketname=bucketname)

    bucket_url = 'https://{bucketname}.s3.amazonaws.com/'.format(bucketname=bucketname)
    return {
        'message': BUILD_STARTED_MSG.format(bucket_url=bucket_url),
        'bucket_url': bucket_url,
        'artifacts': sorted(keys),
    }


def build_wheel(src_key, python_version, bucketname=BUCKET):
    """Build a wheel from provided source, then upload to S3 bucket."""
    fpath, fname = src_key.rsplit('/', 1)
    env = {
        'PYTHON_VERSION': '{v.major}{v.minor}'.format(v=python_version),
        'S3_BASE': 's3://{}/{}'.format(bucketname, fpath),
        'ARCHIVE_NAME': fname,
    }
    # Construct build script
    tplfn = os.path.join(os.path.dirname(__file__), 'build.sh')
    with open(tplfn, encoding='utf8') as tplfp:
        tpl = string.Template(tplfp.read())

    script = tpl.safe_substitute(env)
    # Launch EC2 instance to perform the build in
    launch_params = {
        'ImageId': BUILD_PROXY_AMI,
        'InstanceType': 't2.micro',  # Free tier default
        'MaxCount': 1,
        'MinCount': 1,
        'UserData': script,
        'IamInstanceProfile': {
            'Name': BUILD_PROXY_PROFILE,
        },
        'InstanceInitiatedShutdownBehavior': 'terminate',
    }
    ec2 = boto3.resource('ec2')
    ec2.create_instances(**launch_params)


def clone_packages(requirements, bucketname=BUCKET, overwrite=False):
    """Download packages from pypi, then upload to S3 bucket."""
    rlist = requirements.split() if hasattr(requirements, 'split') else requirements
    cdir = os.path.abspath('/tmp/pipcache')
    try:  # exist_ok=True not available in Python 2.7
        os.makedirs(cdir)
    except OSError:
        pass

    with tempdir() as wdir:
        subprocess.check_call(['pip', 'download', '--cache-dir', cdir] + rlist, cwd=wdir)
        return upload_artifacts(wdir, bucketname)


def upload_artifacts(dirpath, bucketname=BUCKET, overwrite=False):
    """Upload a directory of artifacts to S3 bucket."""
    keys = set()
    # TODO: Potentially run in parallel?
    for fname in os.listdir(dirpath):
        fpath = os.path.join(dirpath, fname)
        key = upload_artifact(fpath, bucketname, overwrite=overwrite)
        keys.add(key)

    return keys


def upload_artifact(filepath, bucketname=BUCKET, overwrite=False):
    """Upload a package artifact to S3 bucket."""
    filename = os.path.basename(filepath)
    key = '{pkg.distribution}/{filename}'.format(
        pkg=PackageInfo.parse(filename),
        filename=filename,
    )
    s3 = boto3.resource('s3')
    obj = s3.Object(bucketname, key)
    if overwrite:
        obj.upload_file(filepath)
    else:
        try:
            obj.load()
        except s3.meta.client.exceptions.ClientError:
            obj.upload_file(filepath)

    return key


class PackageInfo(object):
    """
    Information for a python package artifact.

    See PEP 425 https://www.python.org/dev/peps/pep-0425/
    """

    src_re = re.compile(
        r'(?P<distribution>[^-]+)-(?P<version>[^-]+)'
        r'(?P<ext>\.tar\.[bgx]z|\.zip)'
    )
    whl_re = re.compile(
        r'(?P<distribution>[^-]+)-(?P<version>[^-]+)'
        r'(-(?P<build>\d[^-]*))?'
        r'-(?P<python>[^-]+)-(?P<abi>[^-]+)-(?P<platform>[^-]+)'
        r'(?P<ext>\.whl)'
    )

    def __init__(self, distribution, version, ext, build='', python='', abi='none', platform='any'):
        """Create new PackageInfo object."""
        self.distribution = distribution
        self.version = version
        self.build_tag = build
        self.python_tags = set(python.split('.')) if python else None
        self.abi_tags = set(abi.split('.'))
        self.platform_tags = set(platform.split('.'))
        self.ext = ext

    @classmethod
    def parse(cls, filename):
        """Create a PackageInfo object by parsing an artifact filename."""
        for rgx in (cls.src_re, cls.whl_re):
            match = rgx.match(filename)
            if match:
                return cls(**match.groupdict())

        raise ParseError('Unable to parse filename: ' + filename)

    def is_src(self):
        """Test if this package is source code."""
        return self.ext != '.whl'

    def is_whl(self):
        """Test if this package is a wheel."""
        return self.ext == '.whl'


class ParseError(ValueError):
    """Error raised when unable to parse a string."""


@contextlib.contextmanager
def tempdir():
    """
    Construct a self-destructing temporary directory.

    Usage:
    >>> with tempdir() as tdir:
    ...     # Do stuff.
    """
    wdir = tempfile.mkdtemp()
    yield wdir
    shutil.rmtree(wdir)
