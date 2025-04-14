FROM python:3.9-slim
# Install Tesseract OCR and its dependencies
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev
# ...existing code...
WORKDIR /app
# Copy requirements and install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# Copy remaining project files
COPY . /app
# ...existing code...
# CMD ["flask", "run", "--host=0.0.0.0"]