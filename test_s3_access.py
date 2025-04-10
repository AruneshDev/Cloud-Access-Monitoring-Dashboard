import boto3

s3 = boto3.client('s3')

bucket = 'aws-cloudtrail-logs-342364987304-684f807b'
prefix = 'AWSLogs/342364987304/CloudTrail/'

response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

if 'Contents' in response:
    print("Log files found:")
    for obj in response.get('Contents', [])[:5]:
        print(obj['Key'])
else:
    print("No files found. Check your bucket, prefix, or permissions.")
