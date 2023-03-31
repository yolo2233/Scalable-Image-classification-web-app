import streamlit as st
import requests
from PIL import Image
import io

st.title("Image Classification using ResNet18")

uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

if uploaded_files:
    image_data = []
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        img_bytes = io.BytesIO(uploaded_file.getvalue())
        image_data.append(img_bytes)
    
    if st.button("Predict"):
        response = requests.post(
            "http://backend:80/predict/",
            files=[("images", img_data.getvalue()) for img_data in image_data]
        )
        predictions = response.json()
        pred_highest_prob = []

        for img_pred in predictions:
            pred_highest_prob.append(img_pred[0])

        for img, pred in zip(uploaded_files, pred_highest_prob):
            st.image(img, caption=img.name, use_column_width=True)
            st.write(f"Prediction: {pred[0]}   Probability: {pred[1]}")