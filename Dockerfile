FROM python:3.9

RUN apt-get update && apt-get install -y tzdata
ENV TZ=America/Chicago
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

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
