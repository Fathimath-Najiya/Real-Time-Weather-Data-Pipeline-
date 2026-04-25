import json
import boto3
import os
import urllib.request
from datetime import datetime

API_KEY = os.environ["API_KEY"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
CITIES = ["Kochi", "Bangalore", "Mumbai", "Delhi"]


s3_client = boto3.client("s3")

def lambda_handler(event,context):
    for city in CITIES:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Kochi&appid={API_KEY}&units=metric"

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        file_key = f"raw/weather/{city}/{timestamp}.json"

        s3_client.put_object(
            Bucket = BUCKET_NAME,
            key = file_key,
            Body = json.dumps(data),
            ContentType="application/json" 
        )
    return {"statusCode": 200, "body": "Weather data ingested successfully"}