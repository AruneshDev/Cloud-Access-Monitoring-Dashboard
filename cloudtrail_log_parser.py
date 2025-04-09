import boto3
import json
import pandas as pd
from io import BytesIO
from datetime import datetime

# AWS setup
s3 = boto3.client('s3')
bucket_name = 'your-cloudtrail-log-bucket-name'
prefix = 'AWSLogs/'  # this is default structure

def list_cloudtrail_files(bucket, prefix):
    objects = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj['Key'] for obj in objects.get('Contents', []) if obj['Key'].endswith('.json.gz')]

def extract_events_from_file(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read()
    
    # CloudTrail logs are gzip compressed JSON - this depends on your trail format.
    import gzip
    with gzip.GzipFile(fileobj=BytesIO(content)) as gz:
        data = json.loads(gz.read().decode('utf-8'))
        
    return data.get('Records', [])

def parse_cloudtrail_events(events):
    parsed_data = []
    for event in events:
        parsed_data.append({
            'eventTime': event.get('eventTime'),
            'eventName': event.get('eventName'),
            'userName': event.get('userIdentity', {}).get('userName', 'Unknown'),
            'sourceIPAddress': event.get('sourceIPAddress'),
            'eventSource': event.get('eventSource'),
            'awsRegion': event.get('awsRegion'),
            'userType': event.get('userIdentity', {}).get('type', 'Unknown'),
        })
    return pd.DataFrame(parsed_data)

# MAIN
if __name__ == "__main__":
    print("Fetching CloudTrail logs from S3...")
    files = list_cloudtrail_files(bucket_name, prefix)
    
    all_events = []
    for file_key in files[:10]:  # limit for now
        events = extract_events_from_file(bucket_name, file_key)
        all_events.extend(events)
    
    df = parse_cloudtrail_events(all_events)
    df['eventTime'] = pd.to_datetime(df['eventTime'])

    df.to_csv('parsed_cloudtrail_events.csv', index=False)
    print(f"Extracted {len(df)} events. Saved to parsed_cloudtrail_events.csv")
