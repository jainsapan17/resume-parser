# ============================== #
"""
Status: Working
Author: Sapan Jain
Version: 2.2
Version_updates: 
    - Added conditions to catch errors and updated hyperparameters
    - Added sample resumes
Usage: Python code to analyze uploaded resume against desired job description
Date: 2024-11-26
Dependencies: 
    - Python 3.12
    - other within requirements.txt
"""
# ============================== #
from prompt import SYSTEM_PROMPT
import streamlit as st
import boto3
import json
from io import BytesIO
from datetime import datetime
from botocore.exceptions import ClientError
# ------------------------------- #
AWS_REGION = 'us-east-1'
BUCKET_NAME = 'aws-bucket-name'
MODEL_ID = 'anthropic.claude-v2'
# ------------------------------- #
textract_client = boto3.client('textract', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name=AWS_REGION)
# ------------------------------- #
def extract_resume_text(file_bytes, file_name, bucket_name):
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
def analyze_resume(bedrock_client, model_id, prompt, max_tokens=2000):
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens,
        "temperature": 0.3,
        "top_k": 250,
        "top_p": 0.9,
        "stop_sequences": ["\n\nHuman:"]
    })
    
    response = bedrock_client.invoke_model_with_response_stream(
        modelId=model_id,
        body=body
    )
    
    for event in response.get('body'):
        chunk = json.loads(event['chunk']['bytes'].decode())
        yield chunk['completion']
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
            file_extension = uploaded_file.name.split('.')[-1].lower()
            supported_extensions = ["pdf", "png", "jpg", "jpeg"]
            
            if file_extension not in supported_extensions:
                st.error(f"Unsupported file type: .{file_extension}. Please upload a PDF, PNG, JPG, or JPEG file.")
                return  # Stop execution if file type is not supported

            file_bytes = uploaded_file.read()
            original_filename = uploaded_file.name

            try:
                st.info("Uploading resume to S3 bucket...")
                bucket_name, file_name = upload_to_s3(file_bytes, original_filename)

                if bucket_name is None or file_name is None:
                    st.error("Failed to upload file to S3. Please try again.")
                    return  # Stop execution if S3 upload fails

                st.info("Extracting text from uploaded resume...")
                parsed_text = extract_resume_text(file_bytes, original_filename, bucket_name)

                if not parsed_text:
                    st.error("Failed to extract text from the resume. Please check the file and try again.")
                    return  # Stop execution if text extraction fails

                st.info("Analyzing the resume...")
                prompt = f"{SYSTEM_PROMPT}\n\nHuman: Resume: {parsed_text}\n\nJob Description: {job_description}. Assistant:"
                response_container = st.empty()
                full_response = ""
                for response_chunk in analyze_resume(bedrock_client, MODEL_ID, prompt):
                    full_response += response_chunk
                    response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload a resume to proceed.")
# ------------------------------- #
if __name__ == "__main__":
    main()
