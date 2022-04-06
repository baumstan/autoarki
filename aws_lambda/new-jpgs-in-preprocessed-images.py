import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
sns = boto3.client('sns', region_name='us-west-2')

def lambda_handler(event, context):
    
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key=event['Records'][0]['s3']['object']['key']
    eventname = event['Records'][0]['eventName']
    message = {"key_name": key}

    response = sns.publish(
        TargetArn="arn:aws:sns:us-west-2:499772623536:ImagesReadyTopic",
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )
