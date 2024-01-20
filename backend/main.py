from fastapi import FastAPI, UploadFile
from io import BytesIO
from google.cloud import storage
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from compute.h2oRFE import automl

app = FastAPI()

DATA_BUCKET = "data-test-automate-ml"
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/api/upload")
async def upload(file: UploadFile, fileName):
    try:
        storage_client = storage.Client.from_service_account_json("../credentials.json")

        bucket = storage_client.get_bucket(DATA_BUCKET)
        blob = bucket.blob(f"{fileName}.csv")
        content = await file.read()
        blob.upload_from_string(content)

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

    return {"message": "Data uploaded to Gcloud successfuly"}


@app.get("/api/datasets")
async def getDataSets():
    dataSetNames = []
    try:
        storage_client = storage.Client.from_service_account_json("../credentials.json")

        blobs = storage_client.list_blobs(DATA_BUCKET)
        for blob in blobs:
            dataSetNames.append(blob.name)

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

    return {"names": dataSetNames}


@app.get("/api/data")
async def getData(fileName):
    dataSetLines = ""
    try:
        storage_client = storage.Client.from_service_account_json("../credentials.json")

        bucket = storage_client.get_bucket(DATA_BUCKET)
        blob = bucket.blob(f"{fileName}.csv")

        with blob.open("r") as f:
            dataSetLines = f.read()

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

    return {"data": dataSetLines}

@app.get("/api/automl")
async def getModel(): 
    try:
        storage_client = storage.Client.from_service_account_json("../credentials.json")
        bucket = storage_client.get_bucket("data-test-automate-ml")
        blob = bucket.blob("fish_data.csv")
        byte_stream = BytesIO()
        blob.download_to_file(byte_stream)
        byte_stream.seek(0)
        df = pd.read_csv(byte_stream)
        model_path = automl(df)

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

    return {"model saved to": model_path}