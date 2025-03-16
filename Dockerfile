FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ca-certificates

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --cache-dir=/var/tmp/ torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Set environment variables
ENV GOOGLE_API_KEY="AIzaSyC-zFkoipLIFe-2u4ZlamzwT-wZkHzJx-U"
ENV MONGO_URI="mongodb+srv://temitayoadejuyigbe:nt24AfcE1IWcdPDx@cluster0.ojr0j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# docker run -e MONGO_URI="mongodb+srv://temitayoadejuyigbe:nt24AfcE1IWcdPDx@cluster0.ojr0j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" -p 8000:8000 qa-chatbot

# FROM python:3.9-slim

# WORKDIR /app

# COPY requirements.txt .

# RUN pip3 install --cache-dir=/var/tmp/ torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

