import requests
import os
from pathlib import Path

# GBIF API credentials
username = "cianp"
password = "12june1992"

# Define search parameters
species_name = "Passer domesticus (Linnaeus, 1758)"
api_url = "https://api.gbif.org/v1/occurrence/search"

# Directory to save images
output_dir = Path("gbif_images")
output_dir.mkdir(exist_ok=True)

# Define pagination parameters
limit = 1000  # Maximum GBIF limit
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

    # Extract multimedia URLs from each result
    for result in results:
        if "media" in result:
            for media in result["media"]:
                if media.get("type") == "StillImage":
                    image_urls.append(media.get("identifier"))

    # Break if we've collected 20 URLs
    if len(image_urls) >= 20:
        break

    # Update offset for next batch
    offset += limit

print(f"Found {len(image_urls)} image URLs.")

# Step 2: Download the first 20 images
print("Downloading images...")
for idx, url in enumerate(image_urls[:20]):
    image_path = output_dir / f"image_{idx + 1}.jpg"
    if not url:
        continue
    if image_path.exists():
        print(f"Skipping {image_path.name} (already downloaded)")
        continue
    try:
        img_data = requests.get(url).content
        with open(image_path, "wb") as img_file:
            img_file.write(img_data)
        print(f"Downloaded: {image_path.name}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

print("Image download complete!")

