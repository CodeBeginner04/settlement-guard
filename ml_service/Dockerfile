FROM python:3.10-slim

WORKDIR /app

# Install essential build tools (often needed for ML libs like xgboost/shap)
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "inference:app", "--host", "0.0.0.0", "--port", "8001"]
