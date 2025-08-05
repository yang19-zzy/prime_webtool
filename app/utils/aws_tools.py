import os
import boto3
from botocore.exceptions import ClientError
import json
import pandas as pd
from io import StringIO




# ## Lambda connection
# def connect_lambda(key, secret, region):
#     """Initialize Lambda client."""
#     return boto3.client('lambda', aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)

# lambda_client = connect_lambda()

## S3 connection
def connect_s3(key, secret, region):
    """Initialize S3 client."""
    return boto3.client('s3', aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)

# s3 = connect_s3()

def list_prefix(s3, bucket: str, prefix: str = "", delimiter: str = "") -> list:
    """List all files or folders in a given S3 bucket prefix."""
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter=delimiter)
    return [f.get('Prefix') if delimiter else f.get('Key') for f in response.get('CommonPrefixes', []) or response.get('Contents', [])]

# def list_prefix(s3, bucket, prefix="", delimiter="/"):
#     paginator = s3.get_paginator('list_objects_v2')
#     operation_parameters = {'Bucket': bucket, 'Delimiter': delimiter}
#     if prefix:
#         operation_parameters['Prefix'] = prefix

#     folders = set()
#     for page in paginator.paginate(**operation_parameters):
#         for common_prefix in page.get('CommonPrefixes', []):
#             folders.add(common_prefix.get('Prefix'))

#     return list(folders)

def get_s3_data(s3, bucket: str, schema: str, table: str) -> pd.DataFrame:
    folder = f"{schema}/{table}/"
    df = pd.read_parquet(f"s3://{bucket}/{folder}")
    print('df:', df.head())
    print('df:', df.head(1).to_dict(orient='records'))

    return df.fillna('')  # Modify to return actual DataFrame when needed.


## Whitelist Fetcher
def get_secret(region_name, secret_name, access_key, secret_key):
    """Fetch the whitelist from AWS Secrets Manager."""
    # session = boto3.session.Session()
    # client = session.client(service_name='secretsmanager', region_name=REGION_NAME)
    client = boto3.client(service_name='secretsmanager', region_name=region_name, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    secret = response['SecretString']
    secret = json.loads(secret)
    print(secret)
    print(type(secret))
    return secret.get('umid', [])

def get_session_data(session, key):
    """Fetch data from session."""
    data = session.get(key)
    if data:
        df = pd.DataFrame(data)
        return df
    return None