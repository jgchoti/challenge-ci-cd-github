import pytest
from unittest.mock import patch
from streamlit_app import load_pet_data
from app.scraper import Scraper


class TestDataFunctions:
    @patch("os.path.exists")
    def test_load_pet_data_no_file(self, mock_exists):
        """Test loading data when no CSV file exists"""
        mock_exists.return_value = False
        result = load_pet_data()
        assert result is None


class TestScraperUnit:
    def test_scraper_initialization(self):
        """Test scraper initializes correctly"""
        scraper = Scraper()

        assert scraper.base_url == "https://www.petconnect.be"
        assert (
            scraper.api_base
            == "https://www.petconnect.be/_api/cloud-data/v2/items/query"
        )
        assert scraper.pets_data == []
        assert scraper.auth_token is not None

    def test_create_api_payload(self):
        """Test API payload creation"""
        scraper = Scraper()
        payload = scraper.create_api_payload(offset=10, limit=30)

        assert payload["dataCollectionId"] == "Items"
        assert payload["query"]["paging"]["offset"] == 10
        assert payload["query"]["paging"]["limit"] == 30
        assert payload["environment"] == "LIVE"
        assert payload["appId"] == "d068c8c3-c306-43f0-badf-398db6eaef4e"

    def test_process_array_field(self):
        """Test array field processing"""
        scraper = Scraper()

        assert scraper._process_array_field(["small", "medium"]) == "small, medium"
        assert scraper._process_array_field("large") == "large"
        assert scraper._process_array_field([]) == ""
        assert scraper._process_array_field(None) == ""

    def test_process_pet_data(self):
        """Test pet data processing"""
        scraper = Scraper()

        item = {
            "_id": "pet123",
            "data": {
                "title": "Buddy",
                "breed": "Golden Retriever",
                "size": ["Large"],
                "gender": ["Male"],
                "ageYear": "5",
                "placeOfResidence": "Antwerp",
                "shortDescription": "Friendly dog",
                "image": "buddy.jpg",
                "link-animals-title": "/animals/buddy-golden-retriever",
                "added": "2025-01-01",
            },
        }

        result = scraper.process_pet_data(item)
        assert result["id"] == "pet123"
        assert result["title"] == "Buddy"
        assert result["breed"] == "Golden Retriever"
        assert result["size"] == "Large"
        assert result["gender"] == "Male"
        assert result["age_year"] == "5"
        assert result["place_of_residence"] == "Antwerp"
        assert (
            result["full_url"]
            == "https://www.petconnect.be/animals/buddy-golden-retriever"
        )


if __name__ == "__main__":
    pytest.main([__file__])
