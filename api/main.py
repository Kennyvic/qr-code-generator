from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
from azure.storage.blob import BlobClient
import os
from io import BytesIO

# Loading Environment variable (Azure Blob Storage credentials)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Blob Storage Configuration
BLOB_ACCOUNT_URL = os.getenv("AZURE_BLOB_SAS_URL")
SAS_TOKEN = os.getenv("AZURE_BLOB_SAS_TOKEN")      
container_name = os.getenv("AZURE_CONTAINER_NAME")

@app.post("/generate-qr/")
async def generate_qr(url: str):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate file name
    file_name = f"qr_codes/{url.split('//')[-1]}.png"

    try:
        # Upload to Azure Blob Storage using SAS token
        blob_client = BlobClient(
            account_url=BLOB_ACCOUNT_URL,
            container_name=container_name,
            blob_name=file_name,
            credential=SAS_TOKEN
        )
        blob_client.upload_blob(img_byte_arr, blob_type="BlockBlob", overwrite=True)
        
        # Generate the blob URL
        blob_url = f"{blob_client.url}?{SAS_TOKEN}"
        return {"qr_code_url": blob_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
