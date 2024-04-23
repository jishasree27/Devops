from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import boto3

app = Flask(__name__)

# AWS S3 configuration
S3_BUCKET_NAME = 'YOUR-BUCKET-NAME'
AWS_ACCESS_KEY_ID = 'YOUR-ACCESS KEY-D'
AWS_SECRET_ACCESS_KEY = 'YOUR-SECRET KEY'
AWS_REGION = 'eu-north-1'

# Configure boto3 to use AWS
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)   
# Function to upload image to S3
def upload_to_s3(file):
    try:
        s3.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
        return True
    except Exception as e:
        print("Error uploading file to S3:", e)
        return False

# Route to render upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image upload
@app.route('/upload', methods=['POST']) 
def upload():
    if 'image' not in request.files:
        return redirect(request.url)

    file = request.files['image']

    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        if upload_to_s3(file):
            return redirect(url_for('display_image', filename=filename))
        else:
            return "Error uploading image to S3"
    else:
        return redirect(request.url)

# Route to display uploaded image
@app.route('/uploads/<filename>')
def display_image(filename):
    # Generate a signed URL for the image
    signed_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': filename},
        ExpiresIn=3600  # URL will expire in 1 hour, adjust as needed
    )
    return render_template('index.html', signed_url=signed_url)

if __name__ == '__main__':
    app.run(debug=True)