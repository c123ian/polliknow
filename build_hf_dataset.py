from datasets import load_dataset, Features, Sequence, ClassLabel, Value, Image
import json
import os

def build_hf_dataset(local_folder, dataset_name, class_names=["class0"]):
    """
    local_folder: path with metadata.jsonl + images
    dataset_name: for push_to_hub
    class_names: list of class labels, e.g. ["face"], ["class0"], etc.
    """
    # Step A: Load metadata.jsonl lines into a list
    metadata_path = os.path.join(local_folder, "metadata.jsonl")
    data_entries = []
    with open(metadata_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            data_entries.append(json.loads(line.strip()))

    # Step B: Convert each entry to the final dictionary
    # For example, "image" -> local path, "objects" -> list[dict]
    # If you want to store the local image path in the 'image' column, do:
    records = []
    for entry in data_entries:
        image_path = os.path.join(local_folder, entry["file_name"])
        records.append({
            "image": image_path,
            "objects": entry["objects"]  # already a list of dicts
        })

    # Step C: Create dataset from in-memory data
    from datasets import Dataset, Features, Sequence, ClassLabel, Value, Image
    # The "objects" is a sequence of sub-dicts:
    # each sub-dict => {"bbox": Sequence(float32), "category": ClassLabel(...)}

    features = Features({
        "image": Image(decode=True),  # store image path or load if decode=True
        "objects": Sequence({
            "bbox": Sequence(Value("float32")),
            "category": ClassLabel(names=class_names)
        })
    })

    ds = Dataset.from_list(records, features=features)
    print(ds)
    print(ds.features)
    print(ds[0])

    # Step D: (Optional) push to hub
    ds.push_to_hub(dataset_name, private=True, token="hf_xxxxxxxxxxxxxxxxx")
    return ds


# Example usage:
local_folder = "."  # folder containing images + metadata.jsonl
my_dataset_name = "c123ian/obj_detect_481_vnew_2"  # your hub dataset name
ds = build_hf_dataset(local_folder, my_dataset_name, class_names=["class0"])

# Now `ds` has columns ["image", "objects"]. 
# "objects" is a Sequence => each item has "bbox", "category".
# Perfect for AutoTrain.
