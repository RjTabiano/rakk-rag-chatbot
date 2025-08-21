from typing import Union
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

# Load environment variables from .env file
load_dotenv()


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Welcome to Python FastAPI World!"}

@app.get("/health", status_code=200, response_description="Health Check")
def read_health():
    return {"status": "OK", "message": "Service is running"}

@app.get("/first", status_code=200, response_description="Health Check")
def read_health():
    return {"status": "OK", "message": "Service1 is running"}

# Access the variables using os.getenv()
api_key = os.getenv("API_KEY")
print(f"API Key: {api_key}")

@app.get("/second", status_code=200, response_description="Health Check")
def read_health():
    return {"status": "OK", "message": f"Service2 is running  {api_key}"}

# Access the variables using os.getenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

@app.get("/getsafilename", response_description="Get Storage Account File Name")
def read_safilename():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        container_name = "blob-container"
        container_client = blob_service_client.get_container_client(container_name)

        print("\n getting blobs...")
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            return {f"I see the first blob name is -> {blob.name}"}
    except AzureError as e:
        print(f"Failed to connect or list blob: {e}")

# @app.get("/getsacontainername", response_description="Get first Storage Account Container Name")
# def read_sacontainername():
#     try:
#         blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#         containers = blob_service_client.list_containers()
#         print("Connected! checking first container:")
#         for container in containers:
#             return {f"I see the first container name is -> {container['name']}"}
#     except AzureError as e:
#         print(f"Failed to connect or list first container: {e}")