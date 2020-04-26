"""The service module handles creation/inspection of the remote Vendor service."""
from __future__ import absolute_import

import logging
import os.path
import subprocess
import shutil
import tempfile

import boto3
from packaging import version
import six

from .__about__ import __version__


DEFAULT_DEPLOYMENT_STACK_NAME = 'Vendor-deployment'
DEFAULT_SERVICE_STACK_NAME = 'Vendor'

log = logging.getLogger(__name__)


class StackException(Exception):
    """Base exception class."""

    def __init__(self, stack_name):
        """Create new StackException for stack_name."""
        self.stack_name = stack_name
        super(StackException, self).__init__(stack_name)


class StackNotFound(StackException):
    """CloudFormation stack does not exist."""

    def __str__(self):
        return 'Stack {} not found'.format(self.stack_name)


class StackOutdated(StackException):
    """CloudFormation stack is not up-to-date."""

    def __str__(self):
        return 'Stack {} is outdated'.format(self.stack_name)


def parse_stack_outputs(description):
    """Parse boto output list into dictionary."""
    result = {}
    log.debug('Parsing %r', description)
    for output in description['Outputs']:
        result[output['OutputKey']] = output['OutputValue']

    return result


def run_cloudformation_command(command, **options):
    """Run awscli cloudformation command."""
    pargs = ['aws', 'cloudformation', command]
    for param, value in options.items():
        pargs.append('--' + param.replace('_', '-'))
        if isinstance(value, six.string_types):
            pargs.append(value)
        else:
            pargs.extend(value)

    log.debug(' '.join(pargs))
    return subprocess.check_call(pargs)


def get_deployment_filepath(filename):
    """Return location of filename within deployment code."""
    return os.path.join(os.path.dirname(__file__), 'aws', filename)


class VendorService(object):
    """The Vendor service."""

    version = version.Version(__version__)
    deployment_template = get_deployment_filepath('vendor-deployment.yml')
    service_template = get_deployment_filepath('vendor.yml')

    def __init__(self, cloudformation_client=None):
        """Create new instance of Vendor service."""
        self._describe_cache = {}
        if cloudformation_client:
            self.client = cloudformation_client
        else:
            self.client = boto3.client('cloudformation')

    def describe_stack(self, stack_name):
        """Return stack description."""
        cached = self._describe_cache.get(stack_name)
        if cached:
            log.debug('Returning %s from cache', stack_name)
            return cached

        try:
            response = self.client.describe_stacks(StackName=stack_name)
        except self.client.exceptions.ClientError as exc:
            expect = 'Stack with id {} does not exist'.format(stack_name)
            response = dict(exc.response)  # Make a shallow copy for re-raise
            error = response.pop('Error')
            if error['Message'] == expect:
                response['Stacks'] = []
            else:
                log.exception('Error describing %s', stack_name)
                raise

        stacks = response['Stacks']
        log.info('Stacks found: %r', stacks)
        count = len(stacks)
        if count > 1:
            msg = 'Found {} stacks for name {} (expected 1)'
            raise ValueError(msg.format(count, stack_name))
        elif count < 1:
            raise StackNotFound(stack_name)

        self._describe_cache[stack_name] = stacks[0]
        return stacks[0]

    def check_stack(self, stack_name):
        """Check status of stack."""
        description = self.describe_stack(stack_name)
        # TODO: Check stack deployment status
        # Check version.
        outputs = parse_stack_outputs(description)
        sv = version.parse(outputs['Version'])
        log.debug('Stack version: %s', sv)
        if sv < self.version:
            raise StackOutdated(stack_name)
        elif sv > self.version:
            raise ValueError('Package outdated, please upgrade to at least {}.'.format(sv))

        return description

    def deployment(self, stack_name=DEFAULT_DEPLOYMENT_STACK_NAME):
        """Return Deployment stack information, creating/updating it if necessary."""
        try:
            description = self.check_stack(stack_name)
        except StackException as exc:
            log.info('%s, deploying', exc)
            run_cloudformation_command(
                'deploy',
                stack_name=stack_name,
                template_file=self.deployment_template,
                parameter_overrides='Version={}'.format(self.version),
            )
            description = self.check_stack(stack_name)

        return parse_stack_outputs(description)

    def service(self, stack_name=DEFAULT_SERVICE_STACK_NAME, bucket_name=None, deployment_bucket_name=None):
        """Return service stack information, creating/updating as necessary."""
        if deployment_bucket_name is None:
            deployment_bucket_name = self.deployment()['BucketName']

        try:
            description = self.check_stack(stack_name)
        except StackException as exc:
            log.info('%s, deploying', exc)
            tdir = tempfile.mkdtemp(prefix='vendor-')
            try:
                package_template = os.path.join(
                    tdir, os.path.basename(self.service_template),
                )
                # Package...
                run_cloudformation_command(
                    'package',
                    template_file=self.service_template,
                    s3_bucket=deployment_bucket_name,
                    output_template_file=package_template,
                )
                # ...and deploy.
                parameters = [
                    'Version={}'.format(self.version),
                ]
                if bucket_name:
                    parameters.append('BucketName={}'.format(bucket_name))

                run_cloudformation_command(
                    'deploy',
                    stack_name=stack_name,
                    template_file=package_template,
                    parameter_overrides=parameters,
                    capabilities='CAPABILITY_IAM',
                )
            finally:
                shutil.rmtree(tdir)

            description = self.check_stack(stack_name)

        return parse_stack_outputs(description)

    def delete(self, service_stack_name=DEFAULT_SERVICE_STACK_NAME, deployment_stack_name=DEFAULT_DEPLOYMENT_STACK_NAME):
        """Delete the stacks."""
        for stack_name in (service_stack_name, deployment_stack_name):
            if stack_name:
                run_cloudformation_command('delete-stack', stack_name=stack_name)
