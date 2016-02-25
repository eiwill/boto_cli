#!/usr/bin/python
import argparse
import sys
import boto3
import yaml
import logging

from botocore.utils import fix_s3_host


def run():

    def print_bucket(Bucket):
        session = create_session()

        bucket = session.Bucket(Bucket)

        object_summary_iterator = bucket.objects.all()

        print("Bucket %s keys:" % Bucket)
        for obj in object_summary_iterator:
            print(obj.key)

    def print_object(Bucket, Key):
        session = create_session()
        obj = session.Object(Bucket, Key)
        info = obj.get()
        print("Data %s" % info["Body"].read())

    actions = [
        "create_bucket",
        "put_object",
        "upload_file",
        "copy_object",
        "delete_bucket",
        "delete_object",
        "download_file",
        ("print_bucket", print_bucket),
        ("print_object", print_object),
    ]

    def create_arg_parser():
        parser = argparse.ArgumentParser(description="Boto commond line interface")

        group = parser.add_mutually_exclusive_group()
        parser.add_argument("--id", dest="id", help="friendly authorization name", required=True)

        for action in actions:
            if isinstance(action, tuple):
                action, _ = action
            group.add_argument("--" + action, dest=action, help="command name", nargs="*")

        parser.add_argument("-a", "--address", dest="address", help="service address (<host>:<port>)")
        parser.add_argument("-v", "--verbose", dest="verbose", help="verbose logging", action="store_true")
        return parser

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

    arg_parser = create_arg_parser()
    options = arg_parser.parse_args()

    if options.verbose:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    for key in actions:
        callback = None
        if isinstance(key, tuple):
            key, callback = key

        params = getattr(options, key)
        if params is not None:
            kwargs = {}
            for param in params:
                value = param.split("=")
                if len(value) == 2:
                    kwargs[value[0]] = value[1]
                else:
                    sys.exit("Failed to parse parameter %s" % param)

            if callback:
                cmd = callback
            else:
                session = create_session()
                cmd = getattr(session.meta.client, key)

            if cmd:
                cmd(**kwargs)
            else:
                sys.exit("Failed to find function in boto client")
            break
    else:
        sys.exit("Error: No command")


if __name__ == "__main__":
    run()
