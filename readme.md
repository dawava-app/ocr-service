# OCR Service

A FastAPI-based OCR microservice that extracts medicine names from images using an OCR pipeline. The service accepts an image URL, processes the image, and returns the detected medicine name along with the detected language and confidence score.

## Features

- FastAPI REST API
- OCR-based medicine name extraction
- Image URL support
- Automatic temporary file cleanup
- Docker support
- Clean project architecture
- Pydantic request/response validation

---

## Project Structure

```
.
├── app
│   ├── controllers
│   ├── core
│   ├── models
│   ├── schemas
│   ├── services
│   ├── utils
│   ├── config.py
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
AZURE_OCR_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_OCR_KEY=YOUR_AZURE_KEY
AZURE_OCR_TIMEOUT=30
AZURE_OCR_MAX_POLLS=60
AZURE_OCR_POLL_SECONDS=1
```

> **Do not commit your `.env` file to GitHub.**

---

## Running the Application

### Development

```bash
uvicorn app.main:app --reload
```

API will be available at

```
http://localhost:8000
```

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

## API

### POST `/ocr`

Extract medicine name from an image URL.

### Request

```json
{
    "image_url": "https://example.com/image.jpg"
}
```

### Response

```json
{
    "text": "ERYTHROCIN",
    "language": "en",
    "confidence": 0.98
}
```

---

## Docker

Build

```bash
docker build -t ocr-service .
```

Run

```bash
docker run -p 8000:8000 ocr-service
```

Or using Docker Compose

```bash
docker compose up --build
```

---

## Technology Stack

- FastAPI
- Pydantic
- Uvicorn
- Azure AI Vision OCR
- OpenCV
- Python

---

## Error Handling

The service automatically:

- Downloads the image from the provided URL.
- Processes OCR.
- Deletes temporary files after processing.
- Returns appropriate HTTP errors for invalid requests.

---

## Future Improvements

- Image upload endpoint
- Batch OCR processing
- OCR result caching
- Authentication
- Logging and monitoring
- Unit and integration tests

---

## License

This project is intended for internal use by the Dawava platform.
