Boto3 command line interface
============================

`--id` -- friendly authorization name.
`--put/--get/--delete` -- command name.
`--bucket(-b)` -- bucket name.
`--key(-k)` -- key name.
`--file(-f)` -- path to file.
`--data(-d)` -- string.
`--address(-a)` -- service address (http://<host>:<port>).

Examples:

```
./boto_cli.py --id=personal --put --bucket=test1 --key=123 --file=/test123
```

Will create a bucket and a key.

```
./boto_cli.py --id=personal --put --bucket=test1
```

Will create only bucket.

```
./boto_cli.py --id=personal --get --bucket=1234 --key=1234 --file=/output.txt
```

Download file to the output.txt.

Credentials should be in .credentials.yaml in the same folder, where ./boto_cli.py lies:

```
---
credentials:
  personal:
    id: user123
    key: key3194u029urfoere
```