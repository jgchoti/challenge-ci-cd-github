import requests
import json
import base64
import urllib.parse
import time
import pandas as pd


class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.petconnect.be"
        self.api_base = "https://www.petconnect.be/_api/cloud-data/v2/items/query"
        self.pets_data = []
        self.auth_token = "wixcode-pub.567987c7e8261a094434812c47312ecc4da5f2a6.eyJpbnN0YW5jZUlkIjoiMGVhMzg1OGUtMDU5NC00MTUzLWI0MGEtYjhiMTJkYTEyOTZhIiwiaHRtbFNpdGVJZCI6ImFkMzg5NDk3LTNiMjAtNGE4My05Y2Q0LWYwZDNiNWQ0YjE3YyIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTc1NTUzOTY1NzQ5MSwiYWlkIjoiYWU3ZTczMzUtMWQ3OC00YzE2LTg0NWEtOTQwYmNhYWViMDQyIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjUzM2RkNWVkLTE5MzgtNDY2MC04NjBiLWQ2MmU3YWIxMDhkYiIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsSGFzRG9tYWluLEFkc0ZyZWUiLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiOWE2MWQ5MjItMDFjMy00ZjliLWJhYTYtNzZkODUyZTBjZjNiIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsLCJwZXJtaXNzaW9uU2NvcGUiOm51bGwsImxvZ2luQWNjb3VudElkIjpudWxsLCJpc0xvZ2luQWNjb3VudE93bmVyIjpudWxsLCJib3VuZFNlc3Npb24iOiIxVUw3NGtHd1dBX2dkaloyZ0tZclBSZktmSzlhZFVvN2xFNHJNbWFZNGtFIiwic2Vzc2lvbklkIjpudWxsLCJzZXNzaW9uQ3JlYXRpb25UaW1lIjpudWxsLCJzaXRlQ3JlYXRlZERhdGUiOiIyMDIwLTAxLTI5VDE4OjAxOjM5LjEyMloiLCJhY2NvdW50Q3JlYXRlZERhdGUiOm51bGx9"
        self.common_config = None

    def setup_api_headers(self):
        common_config = {
            "brand": "wix",
            "host": "VIEWER",
            "BSI": "52452dd9-e78b-4d21-b6aa-43a9a9fa0df6|3",
            "siteRevision": "546",
            "renderingFlow": "NONE",
            "language": "en",
            "locale": "en-gb",
        }

        common_config_str = urllib.parse.quote(
            json.dumps(common_config, separators=(",", ":"))
        )

        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "authorization": self.auth_token,
                "commonconfig": common_config_str,
                "dnt": "1",
                "referer": "https://www.petconnect.be/_partials/wix-thunderbolt/dist/clientWorker.8bc85bbc.bundle.min.js",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "x-wix-brand": "wix",
                "x-wix-linguist": "en|en-gb|true|0ea3858e-0594-4153-b40a-b8b12da1296a",
            }
        )

        print("✅ API headers configured")

    def create_api_payload(self, offset=0, limit=20):
        """Create the API payload exactly as shown in the working URL"""
        return {
            "dataCollectionId": "Items",
            "query": {
                "filter": {"statusCheckBoxIfAdopted": {"$ne": True}},
                "sort": [{"fieldName": "added", "order": "DESC"}],
                "paging": {"offset": offset, "limit": limit},
                "fields": [],
            },
            "referencedItemOptions": [],
            "returnTotalCount": True,
            "environment": "LIVE",
            "appId": "d068c8c3-c306-43f0-badf-398db6eaef4e",
        }

    def encode_payload(self, payload):
        """Encode payload exactly as the working URL shows"""

        json_string = json.dumps(payload)
        print(f"JSON payload: {json_string}")
        json_bytes = json_string.encode("utf-8")
        base64_bytes = base64.b64encode(json_bytes)
        base64_string = base64_bytes.decode("utf-8")
        base64_string = base64_string.rstrip("=")
        encoded = urllib.parse.quote(base64_string)

        return encoded

    def fetch_pets_data(self, offset=0, limit=20):
        """Fetch pets data using the authenticated API endpoint"""
        try:
            payload = self.create_api_payload(offset, limit)
            encoded_payload = self.encode_payload(payload)

            url = f"{self.api_base}?.r={encoded_payload}"

            print(f"🔍 Fetching data from offset {offset}, limit {limit}")
            print(f"API URL length: {len(url)}")

            response = self.session.get(url, timeout=30)

            print(f"API Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully received data")
                if "dataItems" in data:
                    print(f"Found {len(data['dataItems'])} items")
                    if "totalCount" in data:
                        print(f"Total available: {data['totalCount']} items")
                return data

            else:
                print(f"❌ API request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Exception during API request: {e}")
            return None

    def process_pet_data(self, item):
        try:
            data = item.get("data", {})
            pet = {
                "id": item.get("_id", ""),
                "title": data.get("title", ""),
                "short_description": data.get("shortDescription", ""),
                "long_description": data.get("longDescription", ""),
                "link": data.get("link-animals-title", ""),
                "breed": data.get("breed", ""),
                "size": self._process_array_field(data.get("size", [])),
                "gender": self._process_array_field(data.get("gender", [])),
                "born": data.get("born", ""),
                "age_year": data.get("ageYear", ""),
                "place_of_residence": data.get("placeOfResidence", ""),
                "main_image": self._convert_wix_image_url(data.get("image", "")),
                "added_date": data.get("added", ""),
                "last_modified": data.get("lastModified", ""),
                "status_adopted": data.get("statusCheckBoxIfAdopted", False),
                "other_fields": {
                    k: v
                    for k, v in data.items()
                    if k
                    not in [
                        "title",
                        "shortDescription",
                        "longDescription",
                        "link-animals-title",
                        "breed",
                        "size",
                        "gender",
                        "born",
                        "ageYear",
                        "placeOfResidence",
                        "image",
                        "picture_galery",
                        "added",
                        "lastModified",
                        "statusCheckBoxIfAdopted",
                    ]
                },
            }

            if pet["link"]:
                pet["full_url"] = f"{self.base_url}{pet['link']}"

            return pet

        except Exception as e:
            print(f"Error processing pet data: {e}")
            print(f"Item data: {item}")
            return None

    def _convert_wix_image_url(self, wix_url):
        if not wix_url or not isinstance(wix_url, str):
            return None

        if wix_url.startswith("wix:image://v1/"):
            try:
                # Remove the wix:image://v1/ prefix
                url_part = wix_url.replace("wix:image://v1/", "")
                # Split by the first '/' to separate image info from filename
                if "/" in url_part:
                    image_info, rest = url_part.split("/", 1)

                    if "#" in rest:
                        params = rest.split("#")[1] if "#" in rest else ""
                        width = 800
                        height = 600
                        if "originWidth=" in params:
                            width = int(params.split("originWidth=")[1].split("&")[0])

                        if "originHeight=" in params:
                            height = int(params.split("originHeight=")[1].split("&")[0])

                    else:
                        width = 800
                        height = 600
                    converted_url = f"https://static.wixstatic.com/media/{image_info}/v1/fit/w_{width},h_{height},q_90,enc_avif,quality_auto/{image_info}"
                    return converted_url
            except Exception as e:
                print(f"Error converting Wix URL {wix_url}: {e}")
                return None

        elif wix_url.startswith("http"):
            return wix_url

        elif wix_url.startswith("/"):
            return f"https://www.petconnect.be{wix_url}"

        return wix_url

    def _process_array_field(self, field_value):
        if isinstance(field_value, list):
            return ", ".join(str(x) for x in field_value)
        return str(field_value) if field_value else ""

    def run_scraper(self, max_items=100):
        print("🐾 Starting authenticated PetConnect.be API scraper...")

        self.setup_api_headers()
        offset = 0
        limit = 20
        total_fetched = 0

        while total_fetched < max_items:
            api_data = self.fetch_pets_data(offset, limit)

            if not api_data:
                print("Failed to fetch data, stopping")
                break

            items = api_data.get("dataItems", [])
            if not items:
                print("No more items available")
                break

            print(f"📋 Processing {len(items)} items...")

            for item in items:
                pet_data = self.process_pet_data(item)
                if pet_data:
                    self.pets_data.append(pet_data)
                    total_fetched = len(self.pets_data)

            if len(items) < limit:
                print("Reached last page")
                break

            offset += limit

            time.sleep(1)

        print(f"✅ Scraping completed! Found {len(self.pets_data)} pets")
        return self.pets_data

    def save_to_csv(self, filename="petconnect_pets.csv"):
        """Save collected data to CSV"""
        if not self.pets_data:
            print("No data to save")
            return

        csv_data = []
        for pet in self.pets_data:
            csv_row = pet.copy()
            if isinstance(csv_row.get("gallery_images"), list):
                csv_row["gallery_images"] = "; ".join(csv_row["gallery_images"])
            csv_row.pop("other_fields", None)
            csv_data.append(csv_row)

        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"💾 Saved {len(df)} records to {filename}")
