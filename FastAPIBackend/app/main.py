from fastapi import FastAPI
from app.model.model import ResNet18
from fastapi import FastAPI, File, UploadFile
from typing import List
import uvicorn
from PIL import Image
import io 
import torch 


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
        img_data = Image.open(io.BytesIO(await img.read())).convert("RGB")
        preprocessed_img = resnet.transform(img_data)
        batch_images.append(preprocessed_img)

    # Prepare input tensor by concatenating all preprocessed images
    input_tensor = torch.stack(batch_images)
    result = resnet.predict_pipeline(input_tensor)
    
    return result


# Run the server
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)