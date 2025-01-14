import requests
import pandas as pd
from pathlib import Path

# GBIF API credentials
username = "cianp"
password = "12june1992"

# Define search parameters
species_name = "Passer domesticus (Linnaeus, 1758)"
api_url = "https://api.gbif.org/v1/occurrence/search"

# Define pagination parameters
limit = 1000
offset = 0

# List to store metadata
metadata = []

print(f"Searching occurrences for '{species_name}'...")

# Step 1: Paginate through results to get multimedia and metadata
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

    # Extract metadata for occurrences with images
    for result in results:
        gbif_id = result.get("gbifID")
        country_code = result.get("countryCode")
        event_date = result.get("eventDate")
        if "media" in result:
            for media in result["media"]:
                if media.get("type") == "StillImage":
                    metadata.append({
                        "gbifID": gbif_id,
                        "imageURL": media.get("identifier"),
                        "countryCode": country_code,
                        "eventDate": event_date
                    })

    # Break if we've collected 20 images
    if len(metadata) >= 20:
        break

    # Update offset for the next batch
    offset += limit

# Step 2: Create a DataFrame and save as CSV
df = pd.DataFrame(metadata)
csv_file = Path(species_name.replace(" ", "_") + "_metadata.csv")
df.to_csv(csv_file, index=False)

# Step 3: Show the DataFrame
print(f"\nMetadata collected for {len(metadata)} images:")
print(df.head())

# Optional: Display the CSV file location
print(f"\nMetadata saved to: {csv_file}")



