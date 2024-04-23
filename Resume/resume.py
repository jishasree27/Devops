from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import boto3
import os

app = Flask(__name__)

# Configurations for Amazon S3
S3_BUCKET_NAME = 'YOUR-BUCKET-NAME'
AWS_ACCESS_KEY_ID = 'YOUR-ACCESS-KEY-ID'
AWS_SECRET_ACCESS_KEY = 'YOUR-SECRET-KEY-ID'
S3_REGION = 'YOUR-AWS-REGION'

# Create an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION
)

# Function to upload file to S3
def upload_to_s3(file_data, file_name):
    s3_client.upload_fileobj(file_data, S3_BUCKET_NAME, file_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    # Add more fields as needed

    # Generate resume content
    resume_content = f"Name: {name}\nEmail: {email}\n"

    # Save resume to a file
    file_name = f"{name}_resume.txt"
    with open(file_name, 'w') as file:
        file.write(resume_content)

    # Upload resume file to S3
    with open(file_name, 'rb') as file_data:
        upload_to_s3(file_data, file_name)

    # Remove the local resume file
    os.remove(file_name)

    return redirect(url_for('download_resume', filename=file_name))

@app.route('/download_resume/<filename>')
def download_resume(filename):
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        try:
            attachment_filename = filename
            content = response['Body'].read()
            return Response(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename="{attachment_filename}"'
                }
            )
        except KeyError:
            # Handle case where filename is not found in the response
            message = "Filename not found in response."
            return render_template('download_resume.html', message=message)
    except Exception as e:
        message = f"An error occurred: {str(e)}"
        return render_template('download_resume.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)