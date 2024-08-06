FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

# # Mount the database volume
# VOLUME /app/cputracker.db

# Define the volume mapping for the "LOGS FOLDER"
VOLUME /app/logs

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
