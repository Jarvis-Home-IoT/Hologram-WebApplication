
===============
 Python Vendor
===============

This package provides an AWS service API for building compiled Python packages,
ready for use in your own AWS Lambda functions.

Requirements
============

In addition to Python package requirements that will automatically be dealt
with during package installation, the vendor package assumes that the AWS CLI
is installed and configured on your system. By default, vendor makes use of
your AWS configuration as the ``aws`` command would.

To install awscli, please refer to the official documentation:
https://docs.aws.amazon.com/cli/latest/userguide/


Installation
============

Programmatic Deployment
-----------------------

The service package module provides a class for dealing with the Vendor stack
deployment. To create the stack using the default settings, simply do the
following:
::
  >>> from vendor.service import VendorService
  >>> vs = VendorService()
  >>> vs.service()
  {'ServiceURL': 'https://abcde01234.execute-api.region.amazonaws.com/api/',
   'Version': '0.1'}

If all goes well, you will get back a dictionary containing the service
``Version`` and the ``ServiceURL``, which can be used to call your newly created
API. If the stacks already exist and are up-to-date, then the function will
simply return the information, rather than recreate it all over again.


Manual Deployment
-----------------

First, deploy the Vendor-deployment stack to prepare a bucket for Serverless
artifacts.
::
  aws cloudformation deploy --stack-name Vendor-deployment --template-file vendor/aws/vendor-deployment.yml

The deployment bucket name can be found from the stack outputs.
::
  aws cloudformation describe-stacks --stack-name Vendor-deployment


Next we can package and deploy the Vendor service.
::
  aws cloudformation package --template-file vendor/aws/vendor.yml --s3-bucket {Vendor-deployment.BucketName} --output-template-file /tmp/vendorpk.yml
  aws cloudformation deploy --stack-name Vendor --template-file /tmp/vendorpk.yml --capabilities CAPABILITY_IAM

Again, the service URL can be found from the stack outputs.
::
  aws cloudformation describe-stacks --stack-name Vendor



Development
===========

Build toolchains
----------------

Because Lambda runs on a readonly filesystem, building is hard as the build
tools are not available on the system. Therefore, we have cheated a little and
instead spawn our own 'Lambda' on a self-destructing EC2 instance. This is done
by passing a script into the EC2 user-data and setting the instance to
terminate on shutdown, which the script does on exit.


