from datasets import load_dataset, Features, Sequence, Value, Dataset
import pandas as pd
import numpy as np

# 1) Load
hf_ds = load_dataset("c123ian/obj_detect_481_v2", split="train")

# 2) Convert to pandas
pdf = hf_ds.to_pandas()

print("Original objects structure:")
print(pdf["objects"].iloc[0])

# 3) Flatten and transform the data
def flatten_objects(objects_list):
    bboxes = []
    categories = []
    for obj in objects_list:
        bboxes.append(list(obj['bbox'].astype(float)))  # Convert numpy array to list and ensure float
        categories.append(int(obj['category']))  # Ensure integer
    return {
        'bbox': bboxes,
        'category': categories
    }

# Transform and flatten
transformed_data = []
for idx, row in pdf.iterrows():
    item = {
        'image': row['image'],
        'bbox': flatten_objects(row['objects'])['bbox'],
        'category': flatten_objects(row['objects'])['category']
    }
    transformed_data.append(item)

new_pdf = pd.DataFrame(transformed_data)

# 4) Define features
features = Features({
    'image': hf_ds.features['image'],
    'bbox': Sequence(Sequence(Value('float32'), length=4)),
    'category': Sequence(Value('int64'))
})

# 5) Convert to dataset
new_hf_ds = Dataset.from_pandas(new_pdf, features=features)

# 6) Verify the conversion
print("\nVerifying dataset before upload:")
print("Features:", new_hf_ds.features)
print("Number of examples:", len(new_hf_ds))
print("Sample example:", new_hf_ds[0])

# 7) Push to Hub
new_hf_ds.push_to_hub(
    "c123ian/obj_detect_481_v3",
    token="hf_xxxxx",  # Your HuggingFace token
    private=True
)

# 8) Verify the upload
print("\nVerifying uploaded dataset:")
uploaded_ds = load_dataset("c123ian/obj_detect_481_v3", split="train")
print("Uploaded features:", uploaded_ds.features)
print("Uploaded size:", len(uploaded_ds))
print("Uploaded sample:", uploaded_ds[0])

# Compare original and uploaded data
print("\nVerifying data consistency:")
print("Original length == Uploaded length:", len(new_hf_ds) == len(uploaded_ds))
print("Sample bbox matches:", new_hf_ds[0]['bbox'] == uploaded_ds[0]['bbox'])
print("Sample category matches:", new_hf_ds[0]['category'] == uploaded_ds[0]['category'])