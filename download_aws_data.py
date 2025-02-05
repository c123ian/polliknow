import os
import sys
import json
import boto3

# Command to run the script:
# python download_aws_data.py <bucket_name> <label_prefix> <image_prefix>
# Example:
# python download_aws_data.py polliknow-trial-bucket Annotated_Data/Photos_Dunsany_11072024/Annotations/Dunsany_11th_annotation/labels/train/ Annotated_Data/Photos_Dunsany_11072024/Photos/


def yolo_to_coco(yolo_bbox, img_width=1000, img_height=1000):
    x_center, y_center, width, height = map(float, yolo_bbox)
    x = (x_center - width / 2) * img_width
    y = (y_center - height / 2) * img_height
    w = width * img_width
    h = height * img_height
    return [round(x, 1), round(y, 1), round(w, 1), round(h, 1)]


def download_metadata(s3_client, bucket_name, label_prefix):
    metadata = []
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=label_prefix)

    for page in pages:
        if "Contents" not in page:
            print(f"No label files found in s3://{bucket_name}/{label_prefix}")
            return []

        for obj in page["Contents"]:
            key = obj["Key"]
            if key.lower().endswith(".txt"):
                try:
                    response = s3_client.get_object(Bucket=bucket_name, Key=key)
                    content = response['Body'].read().decode('utf-8')
                    image_filename = os.path.basename(key).replace('.txt', '.jpg')

                    objects = []
                    for line in content.strip().split('\n'):
                        parts = line.strip().split()
                        if len(parts) == 5:
                            category = int(parts[0])
                            coco_bbox = yolo_to_coco(parts[1:])
                            objects.append({"bbox": coco_bbox, "category": category})

                    if objects:
                        metadata.append({"file_name": image_filename, "objects": objects})
                except Exception as e:
                    print(f"Error processing {key}: {e}")

    with open('metadata.jsonl', 'w') as f:
        for entry in metadata:
            f.write(json.dumps(entry) + '\n')

    print("Metadata saved to metadata.jsonl")
    return {entry['file_name'] for entry in metadata}


def download_images(s3_client, bucket_name, image_prefix, required_images):
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=image_prefix)

    for page in pages:
        if "Contents" not in page:
            print(f"No images found in s3://{bucket_name}/{image_prefix}")
            return

        for obj in page["Contents"]:
            key = obj["Key"]
            filename = os.path.basename(key)
            if filename in required_images:
                try:
                    print(f"Downloading {key} to {filename}")
                    s3_client.download_file(bucket_name, key, filename)
                except Exception as e:
                    print(f"Error downloading {key}: {e}")


def main():
    if len(sys.argv) != 4:
        print("Usage: python download_aws_data.py <bucket_name> <label_prefix> <image_prefix>")
        sys.exit(1)

    bucket_name = sys.argv[1]
    label_prefix = sys.argv[2]
    image_prefix = sys.argv[3]

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN")
    )

    required_images = download_metadata(s3_client, bucket_name, label_prefix)
    download_images(s3_client, bucket_name, image_prefix, required_images)


if __name__ == "__main__":
    main()

