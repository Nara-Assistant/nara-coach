import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv('.env')

aws_access_key_id: str = os.environ["AWS_ACCESS_KEY_ID"]
aws_secret_access_key: str = os.environ["AWS_SECRET_ACCESS_KEY"]
region="us-east-1"

print((aws_access_key_id, aws_secret_access_key, region))

def upload_file(file_name):
    s3 = boto3.client('s3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    try:
        with open(file_name, "rb") as f:
            s3.upload_fileobj(f, "nara-files", os.path.basename(f.name))
    except ClientError as e:
        logging.error(e)
        return False
    return True


