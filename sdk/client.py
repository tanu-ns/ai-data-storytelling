import requests
import os

class DataStoryClient:
    def __init__(self, base_url="http://localhost:8000", email="analyst@example.com"):
        self.base_url = base_url
        self.headers = {"X-User-Email": email}

    def upload_dataset(self, file_path):
        """Uploads a CSV file and returns the dataset object."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.base_url}/datasets/upload", headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()

    def list_datasets(self):
        """Lists all datasets for the user."""
        response = requests.get(f"{self.base_url}/datasets/", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_dataset(self, dataset_id):
        """Gets details of a specific dataset."""
        response = requests.get(f"{self.base_url}/datasets/{dataset_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def generate_insights(self, dataset_id):
        """Triggers insight generation."""
        response = requests.post(f"{self.base_url}/datasets/{dataset_id}/insights", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def generate_story(self, dataset_id):
        """Triggers story generation."""
        response = requests.post(f"{self.base_url}/datasets/{dataset_id}/story", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def chat(self, dataset_id, message):
        """Chat with the dataset."""
        payload = {"message": message}
        response = requests.post(f"{self.base_url}/datasets/{dataset_id}/chat", headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
