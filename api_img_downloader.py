import requests
import os
from pathlib import Path
from urllib.parse import urlparse

# GBIF API credentials
username = "cianp"
password = "12june1992"

# Define search parameters
species_name = "Passer domesticus (Linnaeus, 1758)"
api_url = "https://api.gbif.org/v1/occurrence/search"

# Create a directory named after the scientific name
output_dir = Path(species_name.replace(" ", "_"))
output_dir.mkdir(exist_ok=True)

# Define pagination parameters
limit = 1000
offset = 0
image_urls = []

print(f"Searching occurrences for '{species_name}'...")

# Step 1: Paginate through results to get multimedia URLs
while True:
    response = requests.get(
        api_url,
        params={"scientificName": species_name, "limit": limit, "offset": offset},
        auth=(username, password)
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        break

    results = response.json().get("results", [])
    if not results:
        print("No more results.")
        break

    # Extract multimedia URLs and gbifIDs
    for result in results:
        gbif_id = result.get("gbifID")
        if "media" in result:
            for media in result["media"]:
                if media.get("type") == "StillImage":
                    image_urls.append((media.get("identifier"), gbif_id))

    # Break if we've collected 20 URLs
    if len(image_urls) >= 20:
        break

    # Update offset for the next batch
    offset += limit

print(f"Found {len(image_urls)} image URLs.")

# Step 2: Download the first 20 images
print("Downloading images...")
for idx, (url, gbif_id) in enumerate(image_urls[:20]):
    if not url or not gbif_id:
        continue

    # Extract file extension from the URL
    file_extension = os.path.splitext(urlparse(url).path)[-1]
    if not file_extension:
        file_extension = ".jpg"  # Default to .jpg if no extension found

    # Construct the file path using gbifID and extension
    image_path = output_dir / f"{gbif_id}{file_extension}"
    if image_path.exists():
        print(f"Skipping {image_path.name} (already downloaded)")
        continue

    # Download the image
    try:
        img_data = requests.get(url).content
        with open(image_path, "wb") as img_file:
            img_file.write(img_data)
        print(f"Downloaded: {image_path.name}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

print("Image download complete!")


