import boto3
import os

# ENV VARS you will set in Lambda console
SENDER = os.environ.get('SENDER_EMAIL')
RECIPIENT = os.environ.get('RECIPIENT_EMAIL')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

def lambda_handler(event, context):
    ses = boto3.client('ses', region_name=REGION)
    
    # Custom subject + body
    subject = "🚨 Alert: Anomaly Detected in Cloud Access Logs"
    body_text = (
        "An abnormal login pattern has been detected in your AWS CloudTrail logs.\n\n"
        "Please check the anomaly_events.csv file or dashboard for details.\n"
        "Time: [Triggered Time]\n\n"
        "This alert was generated automatically by your monitoring system."
    )

    try:
        response = ses.send_email(
            Source=SENDER,
            Destination={'ToAddresses': [RECIPIENT]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body_text}}
            }
        )
        print("Alert sent! Message ID:", response['MessageId'])
        return {"statusCode": 200, "body": "Alert sent."}

    except Exception as e:
        print("Error sending email:", e)
        return {"statusCode": 500, "body": str(e)}
