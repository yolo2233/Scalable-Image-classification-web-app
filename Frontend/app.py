import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io 
import requests
import math
import base64
import time 
import json

# Streamlit reruns the entire script every time there's user interaction (e.g., clicking a button). 

css = '''
<style>
    .rounded-img {
        border-radius: 20px;
        width: 200px;
        height: 200px; 
        # max-width: 150px;
    }
    .image-row {
        margin-bottom: 20px;  # Adjust the margin value to control the space between rows
    }
    .image-caption {
        font-size: 12px;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)


def image_to_base64(image: Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")


def display_images_grid(images, predictions):
    num_images = len(images)
    num_cols = 3
    num_rows = math.ceil(num_images / num_cols)
    cnt = 0

    for i in range(num_rows):
        row_start_idx = i * num_cols
        row_end_idx = min((i+1) * num_cols, num_images)
        row_images = images[row_start_idx:row_end_idx]
        

        st.markdown('<div class="image-row">', unsafe_allow_html=True)  # Begin custom container

        cols = st.columns(num_cols)

        for j, image in enumerate(row_images):
            base64_image = image_to_base64(image)
            cols[j].markdown(f'''
                    <img src="data:image/png;base64,{base64_image}" class="rounded-img">
                    <div class="image-caption">{f"{predictions[cnt][0][0]} <br> Confidence: {predictions[cnt][0][1]:.2%}"}</div>
            ''', unsafe_allow_html=True)
            cnt += 1

        # Add spacer column to the end of the row if it's shorter than the maximum row length
        num_spacer_cols = num_cols - len(row_images)
        for k in range(num_spacer_cols):
            cols[-(k+1)].write("")

        st.markdown('</div>', unsafe_allow_html=True) 


def display_image_and_predictions(image, predictions):
    st.image(image, use_column_width=True)
    class_names, confidences = zip(*predictions)
    plt.barh(class_names, confidences)
    plt.xlabel("Confidence")
    plt.ylabel("Class Name")
    plt.xlim(0, 1)
    st.pyplot(plt.gcf())


st.title("Scalable Image Prediction App")

st.write('## Small Batch Image Prediction')

uploaded_files = st.file_uploader("Upload images for ", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="uploaded_files")
if uploaded_files and len(uploaded_files) > 9:
    st.error("Please upload no more than 9 files.")
    raise SystemExit()

if uploaded_files:
    image_data = []
    images = [ Image.open(uploaded_file) for uploaded_file in uploaded_files]

    image_bytes = [io.BytesIO(uploaded_file.getvalue()) for uploaded_file in uploaded_files]

    if st.button("Predict"):
        response = requests.post(
            "http://backend:80/predict/",
            files=[("images", img.getvalue()) for img in image_bytes]
        )
    
        predictions = response.json()
        display_images_grid(images, predictions)


st.write('## Large Batch Image Prediction')
uploaded_file_s3 = st.file_uploader("Upload zip files only", type="zip")

if "upload_s3_clicked" not in st.session_state:
    st.session_state.upload_s3_clicked = False


if uploaded_file_s3:
    if st.button("Upload to AWS S3"):
        files = {"file": (uploaded_file_s3.name, uploaded_file_s3, uploaded_file_s3.type)}
        response = requests.post("http://backend:80/upload", files=files)
        if response.status_code == 200:
            st.write(f"File {uploaded_file_s3.name} uploaded successfully.")
        else:
            st.write(f"Error uploading {uploaded_file_s3.name}.")


        st.session_state.upload_s3_clicked = True



if st.session_state.upload_s3_clicked:
    if st.button("Batch predict"):
        with st.spinner(f"Predicting {uploaded_file_s3.name} ... "):
            response = requests.post("http://backend:80/predict-batch", json={"file_name": uploaded_file_s3.name})

            json_content = response.json()

            if json_content["type"] == "json":
                # Convert JSON content to a string
                json_string = json.dumps(json_content, indent=2)
                # Create a download button for the JSON file
                st.download_button("Download Prediction File", json_string, "prediction.json", "application/json")
            else:
                st.write(json_content["content"])
            if response.status_code == 422:
                print(response.json())


