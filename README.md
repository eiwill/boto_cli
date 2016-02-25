Boto3 command line interface
============================

```
  -h, --help            show this help message and exit
  --id ID               friendly authorization name
  --create_bucket [CREATE_BUCKET [CREATE_BUCKET ...]]
                        command name
  --put_object [PUT_OBJECT [PUT_OBJECT ...]]
                        command name
  --upload_file [UPLOAD_FILE [UPLOAD_FILE ...]]
                        command name
  --copy_object [COPY_OBJECT [COPY_OBJECT ...]]
                        command name
  --delete_bucket [DELETE_BUCKET [DELETE_BUCKET ...]]
                        command name
  --delete_object [DELETE_OBJECT [DELETE_OBJECT ...]]
                        command name
  --download_file [DOWNLOAD_FILE [DOWNLOAD_FILE ...]]
                        command name
  --print_bucket [PRINT_BUCKET [PRINT_BUCKET ...]]
                        command name
  --print_object [PRINT_OBJECT [PRINT_OBJECT ...]]
                        command name
  -a ADDRESS, --address ADDRESS
                        service address (<host>:<port>)
  -v, --verbose         verbose logging
```

Examples:


Download file:

```
./boto_cli.py --id user1 -v --download_file Bucket=1234 Key=1234 Filename=file
```


Create bucket: 

```
./boto_cli.py --id user1 -v --create_bucket Bucket=123434 ACL=public-read
```



Credentials should be in .credentials.yaml in the same folder, where ./boto_cli.py lies:

```
---
credentials:
  user1:
    id: user123
    key: key3194u029urfoere
```