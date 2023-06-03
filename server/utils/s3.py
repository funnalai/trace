
import boto3
import os


async def upload_image_to_s3(image_file, bucket_name, key):
    try:
        # Create an S3 client
        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv(
                              "AWS_SECRET_ACCESS_KEY"),
                          )

        # Upload the image file to the specified bucket with the given key
        result = s3.upload_fileobj(image_file, bucket_name, str(key))
        print(result)
        return f"""https://{bucket_name}.s3.{os.getenv("AWS_REGION")}.amazonaws.com/{key}"""
    except Exception as ex:
        print("Error uploading image to s3: ", ex)
        raise ex


# Usage example
# image_file = 'path/to/image.jpg'  # Replace with the actual path to your image file
# bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
# # Replace with the desired key or path of the image in the bucket
# key = 'images/image.jpg'

# upload_image_to_s3(image_file, bucket_name, key)
