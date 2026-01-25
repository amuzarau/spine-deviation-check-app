# --- Base image ---
FROM python:3.11-slim

# --- System dependencies for OpenCV / MediaPipe ---
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    libx11-6 \
    libxau6 \
    libxdmcp6 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# --- Set workdir ---
WORKDIR /app

# --- Copy requirements first (better cache) ---
COPY requirements.txt .

# --- Install Python deps ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy app code ---
COPY . .

# --- Expose port (Render/Railway use $PORT) ---
EXPOSE 8000

# --- Run FastAPI ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
