FROM python:3.12-alpine AS builder
WORKDIR /app
COPY requirements.txt . 
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . .

FROM builder AS test
CMD ["python", "-m", "pytest"]

FROM python:3.12-alpine AS prod
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder app/src src  
CMD ["uvicorn", "--app-dir", "src",  "main:app",  "--host",  "0.0.0.0",  "--port",  "8000"]