import boto3
import io
import os

# Initialize the S3 and Rekognition clients
rekognition = boto3.client(
    'rekognition',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
s3 = boto3.client(
    's3',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

# Specify the S3 bucket name and image file (object) name
bucket_name = 'clipperth25'  # Replace with your S3 bucket name
s3_object_name = 'penguin.png'  # Replace with the file name in your S3 bucket

# Download the image from the S3 bucket into memory
image_object = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
image_data = image_object['Body'].read()  # Read the image data into memory

# Call Amazon Rekognition to detect objects in the image
response = rekognition.detect_labels(
    Image={'Bytes': image_data},  # Provide the image data as bytes
    MaxLabels=10,                 # Limit the number of labels returned (e.g., 10 labels)
    MinConfidence=75              # Set a minimum confidence threshold for detection (optional)
)

# Print out the recognized labels (objects) in the image
print(f"Detected labels in the image '{s3_object_name}':")
for label in response['Labels']:
    print(f"Label: {label['Name']}")
    for instance in label['Instances']:
        if 'BoundingBox' in instance:
            print(f"Bounding Box: {instance['BoundingBox']}")

