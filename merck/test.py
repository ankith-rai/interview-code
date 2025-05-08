# lambda function to read s3 objects and get the count

import boto3
s3_client = boto3.client('s3') # initialised once -> Design pattern

def lambda_handler(event, context):
    bucket_name = event.get('bucket_name')
    
    if not bucket_name:
        return {
            'statusCode': 400,
            'body': 'Bucket name not provided in the event input.'
        }

    s3 = boto3.client('s3')
    object_count = 0
    continuation_token = None

    try:
        while True:
            if continuation_token:
                response = s3.list_objects_v2(Bucket=bucket_name, ContinuationToken=continuation_token)
            else:
                response = s3.list_objects_v2(Bucket=bucket_name)
            
            contents = response.get('Contents', [])
            object_count += len(contents)

            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break

        return {
            'statusCode': 200,
            'bucket': bucket_name,
            'object_count': object_count
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
