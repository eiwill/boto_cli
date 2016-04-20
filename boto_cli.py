#!/usr/bin/env python
import argparse
import sys
import boto3
import yaml
import logging
import json

from botocore.utils import fix_s3_host


def run():

    def print_bucket(Bucket, Limit=-1):
        """
        Prints bucket contents
        :param Bucket: name to search
        """
        session = create_session()

        bucket = session.Bucket(Bucket)

        object_summary_iterator = bucket.objects.all()

        print("Bucket %s keys:" % Bucket)
        count = 0
        for obj in object_summary_iterator:
            print(obj.key)
            count += 1
            if Limit != -1 and count > int(Limit):
                break
        print("Count %s" % count)

    def print_object(Bucket, Key):
        """
        Prints object data
        :param Bucket: bucket name
        :param Key: object key
        """
        session = create_session()
        obj = session.Object(Bucket, Key)
        info = obj.get()
        print("Data %s" % info["Body"].read())

    def print_buckets(Prefix=None):
        session = create_session()
        print("Buckets:")
        if Prefix:
            buckets = session.buckets.filter(Prefix=Prefix)
        else:
            buckets = session.buckets.all()
        for bucket in buckets:
            print("%s, %s" % (bucket.name, str(bucket.creation_date)))

    def get_bucket_acl(**kwargs):
        """
        Prints bucket acl
        :param Bucket: bucket name
        """
        session = create_session()
        obj = session.meta.client.get_bucket_acl(**kwargs)
        print("ACL:\n%s" % json.dumps(obj, indent=4))

    def get_object_acl(**kwargs):
        """
        Prints object acl
        :param Bucket: bucket name
        :param Key: object key
        """
        session = create_session()
        obj = session.meta.client.get_object_acl(**kwargs)
        print("ACL:\n%s" % json.dumps(obj, indent=4))

    def show_help(command_name):
        callback = None
        session = create_session()
        for act in actions:
            if isinstance(act, tuple):
                act, callback = act
            else:
                callback = getattr(session.meta.client, act)
            if act == command_name:
                break
        help(callback)

    actions = [
        "create_bucket",
        "put_object",
        "upload_file",
        "copy_object",
        "delete_bucket",
        "delete_object",
        "download_file",
        "put_bucket_acl",
        "put_object_acl",
        ("print_bucket", print_bucket),
        ("print_object", print_object),
        ("print_buckets", print_buckets),
        ("get_bucket_acl", get_bucket_acl),
        ("get_object_acl", get_object_acl),
    ]

    def create_arg_parser():
        parser = argparse.ArgumentParser(description="Boto commond line interface")

        group = parser.add_mutually_exclusive_group()
        parser.add_argument("--id", dest="id", help="friendly authorization name", required=True)

        for action in actions:
            if isinstance(action, tuple):
                action, _ = action
            group.add_argument("--" + action, dest=action, help="command name", nargs="*")

        group.add_argument("--show_help", dest="help", help="show help for command" )
        parser.add_argument("-a", "--address", dest="address", help="service address (<host>:<port>)")
        parser.add_argument("-v", "--verbose", dest="verbose", help="verbose logging", action="store_true")
        parser.add_argument("-r", "--region", dest="region", help="region name")
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
        kwargs = {}
        if options.region:
            kwargs["region_name"] = options.region
        s = boto3.Session(
            aws_access_key_id=creds["id"],
            aws_secret_access_key=creds["key"],
            **kwargs
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

    if options.help:
        show_help(options.help)
        sys.exit(0)

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
                    try:
                        v = json.loads(value[1])
                    except:
                        v = value[1]
                    kwargs[value[0]] = v
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
