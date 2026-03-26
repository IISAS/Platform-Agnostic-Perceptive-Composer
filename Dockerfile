FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    openai \
    "polars[database]" \
    connectorx \
    pydantic

COPY . .

EXPOSE 6969

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6969"]