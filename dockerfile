FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --retries 10 --timeout 120 -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]