# Resume Analyzer

## Description
The Resume Analyzer is a Python application that analyzes uploaded resumes against desired job descriptions. It uses AWS services to extract text from resumes and leverages AI to provide insights on how well the resume matches the job requirements.

## Dependencies
- Python 3.12
- streamlit
- boto3
- pandas
- textract-trp
- botocore
- amazon-textract-response-parser

## AWS Services Used
- Amazon Textract
- Amazon S3
- Amazon Bedrock

## Features
1. Enter desired job role and description
2. Upload resume (PDF, PNG, JPG, JPEG)
3. Analyze resume against job description
4. Provide AI-generated insights on resume-job match

## Setup
1. Ensure you have Python 3.12 installed
2. [Optional] Create a virtualenv
    - `python3 -m venv .venv`
	- `source .venv/bin/activate`
3. Install required dependencies:
	- `pip install -r requirements.txt`
4. Set up AWS credentials with access to Textract, S3, and Bedrock services
5. Configure AWS region and S3 bucket name in the script

## Inputs
- AWS_REGION : Provide the AWS region where you want to run this application
- BUCKET_NAME : Provide the existing S3 bucket name which will be used to store the uploaded resume
- MODEL_ID : Provide the Bedrock AI Model ID that you want to use. Current default is 'anthropic.claude-v2'
	- *Please note that if you update the MODEL_ID, then do update the prompt within code to match the required syntax of the choosen model*

## Usage
1. Run the Streamlit app:
	- `streamlit run app.py`
2. Open the provided URL in your web browser
3. Enter the desired job description
4. Upload your resume
5. View the analysis results

## File Structure
- `app.py`: Main application script
- `prompt.py`: Contains the system prompt for AI analysis
- `requirements.txt`: List of Python dependencies

## Notes
- Ensure you have proper AWS permissions and credentials set up
- The application uses Streamlit for the user interface
- Resume text is extracted using Amazon Textract
- Resumes are temporarily stored in an S3 bucket for processing
- Analysis is performed using Amazon Bedrock's Claude v2 model

## Status
Working

## Author
Sapan Jain

## Version
2.0

## Date
2024-11-26

## License

Copyright (c) 2024 Sapan Jain

All rights reserved.

This software and associated documentation files (the "Software") are the proprietary property of Sapan Jain. The Software is protected by copyright laws and international copyright treaties, as well as other intellectual property laws and treaties.

Unauthorized copying, modification, distribution, or use of this Software, via any medium, is strictly prohibited without the express written permission of the copyright holder.

The Software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the author or copyright holder be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.

Any use of this Software is at your own risk. The author is not responsible for any damages, losses, or consequences that may arise from the use, misuse, or malfunction of the Software. By using this Software, you acknowledge and agree that you assume all risks associated with its use and that the author shall not be held liable for any direct, indirect, incidental, special, exemplary, or consequential damages resulting from the use or inability to use the Software.

For permission requests, please contact: Sapan Jain at jainsapan171@gmail.com
