FROM python:3.8

WORKDIR /app

COPY . .

ENV U2NET_HOME=/app/unet

RUN wget https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx -O /app/unet
RUN apt-get update 
RUN apt-get -y install tesseract-ocr
RUN apt-get -y install libtesseract-dev
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

CMD python3 manage.py runserver 0.0.0.0:$PORT
## CMD python3 scripts/pdf_to_pages_embeddings.py

# EXPOSE 8080/tcp