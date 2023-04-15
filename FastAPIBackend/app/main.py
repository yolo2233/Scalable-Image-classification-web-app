from fastapi import FastAPI
from app.model.model import ResNet18
from fastapi import FastAPI, File, UploadFile
from typing import List
import uvicorn
from PIL import Image
import io 
import torch 
import boto3
from botocore.exceptions import NoCredentialsError
from pydantic import BaseModel
import time
from typing import List, Union
from fastapi.responses import JSONResponse
from torchvision import transforms
from io import BytesIO

app = FastAPI()


@app.get("/")
def home():
    return "Welcome to my image classification task"


@app.post("/predict")
async def predict(images: List[UploadFile] = File(...)):
    resnet = ResNet18()
    batch_images = []
    # Preprocess all images and store them in batch_images
    for img in images:
        img_data = Image.open(BytesIO(await img.read())).convert("RGB")
        preprocessed_img = resnet.transform(img_data)
        batch_images.append(preprocessed_img)

    # Prepare input tensor by concatenating all preprocessed images
    input_tensor = torch.stack(batch_images)
    result = resnet.predict_pipeline(input_tensor)

    return result

ACCESS_KEY = "AKIAXALPLSRWKNMPGJWG"
SECRET_KEY = "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"
s3 = boto3.client("s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name="eu-north-1")


def upload_to_s3(file, bucket, file_name):
    try:
        s3.upload_fileobj(file, bucket, file_name)
    except FileNotFoundError:
        raise FileNotFoundError("The file was not found")
    except NoCredentialsError:
        raise NoCredentialsError("Credentials not available")


class JsonData(BaseModel):
    data: dict


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_to_s3(file.file, "image-classification-app-store", file.filename)
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully."})
    except Exception as e:
        print(f"Error uploading file: {e}")
        return JSONResponse(status_code=500, content={"message": f"Error uploading file: {e}"})




def predict_image_from_s3(bucket, key):
    resnet = ResNet18()
    response = s3.get_object(Bucket=bucket, Key=key)
    tensor_buffer = BytesIO(response['Body'].read())
    loaded_normalized_tensor = torch.load(tensor_buffer)
    # Load the image into a PIL Image object

    img = loaded_normalized_tensor.unsqueeze(0)
    result = resnet.predict_pipeline(img)

    return result

class FileName(BaseModel):
    file_name: str

class StringResponse(BaseModel):
    type: str
    content: str

class JsonResponseModel(BaseModel):
    type: str
    content: dict

ResponseModel = Union[StringResponse, JsonResponseModel]

@app.post("/predict-batch", response_model=ResponseModel) 
async def predict_batch(msg: FileName) -> ResponseModel:
    content = {}
    zip_file=msg.file_name
    content[zip_file] = []
    response_from_s3 = s3.list_objects_v2(Bucket="image-classification-app-store", Prefix=f"processed/{zip_file}/")
    print(response_from_s3, type(response_from_s3))

    if "Contents" in response_from_s3:
        for item in response_from_s3['Contents']:
            image_ele = []
            image_key = item['Key']

            image_ele.append(image_key.split('/')[-1])
            if image_key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                predicted_class = predict_image_from_s3("image-classification-app-store", image_key)
                image_ele.append(predicted_class[0])
                content[zip_file].append(image_ele)
        response_content = {
            "type": "json",
            "content": content
            }
        response = JSONResponse(response_content)
        response.headers["Content-Disposition"] = "attachment; filename=prediction.json"

        return response
    else: 
        return {"type": "string", "content": "Data is being preprocessed on cloud. Try again later."} 

        


# Run the server
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)
