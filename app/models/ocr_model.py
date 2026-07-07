from ultralytics import YOLO
import easyocr
from app.config import YOLO_MODEL_PATH, OCR_LANG, GPU

class OCRModels:

    def __init__(self):
        self.detector = YOLO(YOLO_MODEL_PATH)
        self.reader = easyocr.Reader(OCR_LANG, gpu=GPU)

models = OCRModels()