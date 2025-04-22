import requests

# URL for India ADM1 (state-level) GeoJSON from HDX:
GEOURL = (
    "https://data.humdata.org/dataset/"
    "geoboundaries-admin-boundaries-for-india/"
    "resource/82dc0f1f-d39d-4a78-84a1-a52a65843f3b/"
    "download/geoBoundaries-IND-ADM1.geojson"
)

def download_geojson(url: str, out_path: str = "india_states_geojson.json"):
    """
    Downloads the GeoJSON from the given URL and saves it to out_path.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"Saved GeoJSON to {out_path}")

if __name__ == "__main__":
    download_geojson(GEOURL)
