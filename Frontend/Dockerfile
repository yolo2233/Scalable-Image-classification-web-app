FROM python:3.8

WORKDIR /app 

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

EXPOSE 8501

ENTRYPOINT ["streamlit","run"]

CMD ["app.py", "--server.maxUploadSize", "500"]