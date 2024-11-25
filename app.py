# ============================== #
"""
Status: working
Author: Sapan Jain
Version: 1.1
Version_updates: Creating 1st version to perform document analysis
Usage: Python code to analyze uploaded document
Date: 2024-11-25
Dependencies: 
    - Python 3.12
    - other within requirements.txt
"""
# ============================== #
import streamlit as st
import boto3
import pandas as pd
import time
from io import BytesIO
from datetime import datetime
from botocore.exceptions import ClientError
# ------------------------------- #
AWS_REGION = 'us-east-1'
BUCKET_NAME = 'sapanjai-test-bucket'
# ------------------------------- #
textract_client = boto3.client('textract', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
# ------------------------------- #
def analyze_document(file_bytes, file_name, bucket_name):
    try:
        response = textract_client.detect_document_text(
            Document={
                'Bytes': file_bytes,
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': file_name,
                }
            }
        )
        print('Analyzed document')

        # Extract QUERY_RESULT blocks
        extracted_text = ' '.join([item['Text'] for item in response['Blocks'] if item['BlockType'] == 'LINE'])
        print('Resume parsed successfully')
        return extracted_text

    except ClientError as e:
        st.error(f"AWS Textract error: {e}")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {}
# ------------------------------- #
def upload_to_s3(file_bytes, original_filename, bucket_name=BUCKET_NAME):
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_name, extension = original_filename.rsplit('.', 1)
    sanitized_base_name = base_name.replace(' ', '_')
    file_name = f'{sanitized_base_name}_{date_str}.{extension}'
    print(file_name)
    try:
        s3_client.upload_fileobj(BytesIO(file_bytes), bucket_name, file_name)
        return bucket_name, file_name
    except ClientError as e:
        st.error(f"Error uploading file to S3: {e}")
        return None, None
# ------------------------------- #
def main():
    st.title("Resume Analyzer")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        original_filename = uploaded_file.name
        try:
            st.write("Uploading file to S3 bucket...")
            bucket_name, file_name = upload_to_s3(file_bytes, original_filename)

            st.write("Extracting text from uploaded document...")
            parsed_text = analyze_document(file_bytes, original_filename, bucket_name)

            st.subheader("Extracted Text:")
            st.write(parsed_text)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# ------------------------------- #
if __name__ == "__main__":
    main()
