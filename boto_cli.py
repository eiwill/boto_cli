#!/usr/bin/python
import argparse
import sys
import boto3
import yaml

from botocore.exceptions import ClientError
from botocore.utils import fix_s3_host


def run():
    actions = {}

    def command(name):
        def decorator(f):
            actions[name] = f
            return f

        return decorator

    def create_arg_parser():
        parser = argparse.ArgumentParser(description="Boto commond line interface")

        group = parser.add_mutually_exclusive_group()
        parser.add_argument("--id", dest="id", help="friendly authorization name", required=True)

        for action in actions:
            group.add_argument("--" + action, dest=action, help="command name", action="store_true")

        parser.add_argument("-b", "--bucket", dest="bucket", help="bucket name", required=True)
        parser.add_argument("-k", "--key", dest="key", help="key name")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--file", dest="file", help="path to file")
        group.add_argument("-d", "--data", dest="data", help="string")
        parser.add_argument("-a", "--address", dest="address", help="service address (<host>:<port>)")
        parser.add_argument("-v", "--verbose", dest="verbose", help="verbose logging", action="store_true")
        return parser

    def log(string):
        if options.verbose:
            print(string)

    def create_session():
        # Get parameters from file
        with open(".credentials.yaml", 'r') as stream:
            creds = yaml.load(stream)

        if options.id in creds["credentials"]:
            creds = creds["credentials"][options.id]
        else:
            sys.exit("Error: Invalid id")

        # Create session
        s = boto3.Session(
            aws_access_key_id=creds["id"],
            aws_secret_access_key=creds["key"],
        )

        kwargs = {}
        if options.address:
            kwargs["endpoint_url"] = options.address
        s3 = s.resource('s3', **kwargs)

        if options.address:
            s3.meta.client.meta.events.unregister('before-sign.s3', fix_s3_host)

        return s3

    @command("put")
    def put():
        if options.key and options.file is None and options.data is None:
            sys.exit("Error: Put without data or file")

        session = create_session()

        bucket = session.Bucket(options.bucket)

        try:
            bucket.create()
            log("Bucket %s was created" % options.bucket)
        except ClientError, e:
            if e.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
                sys.exit("Error: Failed to create bucket %s" % e)

        # Put data or file if needed
        if options.data:
            bucket.put_object(Body=options.data, Key=options.key)
            log("Data was uploaded. Size of data = %s" % len(options.data))
        else:
            bucket.upload_file(options.file, options.key)
            log("File %s was uploaded" % options.file)

    @command("get")
    def get():
        session = create_session()

        bucket = session.Bucket(options.bucket)

        object_summary_iterator = bucket.objects.all()

        # Get bucket information
        if options.key:
            if options.file:
                bucket.download_file(options.key, options.file)
                log("File %s was downloaded" % options.file)
            else:
                obj = session.Object(options.bucket, options.key)
                info = obj.get()
                log("Data %s" % info["Body"].read())
        else:
            print("Bucket %s keys:" % options.bucket)
            for obj in object_summary_iterator:
                print(obj.key)

    @command("delete")
    def delete():
        session = create_session()

        bucket = session.Bucket(options.bucket)

        if options.key:
            # Clear key
            obj = session.Object(options.bucket, options.key)
            obj.delete()
            log("Object %s was deleted" % options.key)
        else:
            # Clear bucket
            if len(list(bucket.objects.all())) != 0:
                res = raw_input("Do you want to delete all keys from bucket? [y/n]:\n")
                if res == "y":
                    bucket.objects.delete()
                    log("Bucket %s was deleted" % options.bucket)
                else:
                    sys.exit("Aborted deletion")

            session.meta.client.delete_bucket(Bucket=options.bucket)

    arg_parser = create_arg_parser()
    options = arg_parser.parse_args()

    for key, cmd in actions.iteritems():
        if getattr(options, key):
            cmd()
            break
    else:
        sys.exit("Error: No command")


if __name__ == "__main__":
    run()
