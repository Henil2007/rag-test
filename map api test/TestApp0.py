import requests
import json

API_KEY = "YOUR_API_KEY_HERE"


# -----------------------------
# Load category mapping
# -----------------------------

with open("category_mapper.json", "r", encoding="utf-8") as file:
    categories = json.load(file)


# -----------------------------
# User input
# -----------------------------

location = input("Enter location: ").strip().lower()
business = input("Enter business type: ").strip().lower()
radius = float(input("Enter radius in km: "))


# -----------------------------
# Find category
# -----------------------------

if business not in categories:

    print("\nBusiness type not found.")

    print("\nSupported examples:")

    for name in list(categories.keys())[:30]:
        print("-", name)

    print("\nAdd your business type to category_mapper.json.")

    exit()


category = categories[business]

print(f"\nSearching category: {category}")


# -----------------------------
# Geocode location
# -----------------------------

geocode_url = "https://api.geoapify.com/v1/geocode/search"

geocode_params = {
    "text": location,
    "apiKey": API_KEY
}

response = requests.get(
    geocode_url,
    params=geocode_params
)

if response.status_code != 200:
    print("Geocoding error:")
    print(response.text)
    exit()


data = response.json()

if not data["features"]:
    print("Location not found.")
    exit()


coordinates = data["features"][0]["geometry"]["coordinates"]

longitude = coordinates[0]
latitude = coordinates[1]

print(f"Location found: {latitude}, {longitude}")


# -----------------------------
# Search places
# -----------------------------

places_url = "https://api.geoapify.com/v2/places"

places_params = {
    "categories": category,
    "filter": f"circle:{longitude},{latitude},{radius * 1000}",
    "bias": f"proximity:{longitude},{latitude}",
    "limit": 20,
    "apiKey": API_KEY
}

response = requests.get(
    places_url,
    params=places_params
)

if response.status_code != 200:
    print("\nPlaces API error:")
    print(response.text)
    exit()


places = response.json()["features"]


# -----------------------------
# Display results
# -----------------------------

print(f"\nFound {len(places)} businesses:\n")


for i, place in enumerate(places, 1):

    p = place["properties"]

    name = p.get("name", "Unknown")
    address = p.get("formatted", "Unknown")
    lat = p.get("lat", "Unknown")
    lon = p.get("lon", "Unknown")

    print(f"{i}. {name}")
    print(f"   Address: {address}")
    print(f"   Location: {lat}, {lon}")
    print()

