FROM python:3.9

# Install Streamlit
RUN pip install streamlit

# Create a directory for your application code
WORKDIR /app

# Copy your application code
COPY . /app

# Define the volume mapping for the "LOGS FOLDER"
VOLUME /app/logs

# Run the Streamlit app
#CMD ["streamlit", "run", "sl_hw.py"]
CMD ["streamlit", "run", "app.py"]
