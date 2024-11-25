# ============================== #
"""
Status: working
Author: Sapan Jain
Version: 1.2
Version_updates: Get Job role as input
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
def parse_resume(text):
    # Placeholder for resume parsing logic
    # This function should be implemented based on the specific resume format
    # and the desired output
    # For demonstration purposes, we'll just return the text as-is
    pass
# ------------------------------- #
def main():
    st.title("Resume Analyzer")

    # Use session state to track form submission
    if "form_submitted" not in st.session_state:
        st.session_state["form_submitted"] = False

    # 1. Enter Desired Job Role ----->>>
    with st.form("job_description_form"):
        # Multi-line text area
        job_description = st.text_area(
            "Enter your desired job role and its description:",
            height=300,
        )
        # Submit button
        job_description_submitted = st.form_submit_button("Submit")

    if job_description_submitted:
        # Persist form submission state
        st.session_state["form_submitted"] = True
        st.session_state["job_description"] = job_description
        st.success("Job description submitted successfully!")

    # 2. Upload Resume ----->>>
    if st.session_state.get("form_submitted", False):
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "png", "jpg", "jpeg"],
        )

        # 3. Analyze Resume ----->>>
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            original_filename = uploaded_file.name

            try:
                st.info("Uploading resume to S3 bucket...")
                bucket_name, file_name = upload_to_s3(file_bytes, original_filename)

                st.info("Extracting text from uploaded resume...")
                parsed_text = analyze_document(file_bytes, original_filename, bucket_name)

                st.subheader("Extracted Text:")
                st.write(parsed_text)

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload a resume to proceed.")


# ------------------------------- #
if __name__ == "__main__":
    main()
