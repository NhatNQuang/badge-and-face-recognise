from fastapi import FastAPI, File, UploadFile
from functions import detect_human_by_image

app = FastAPI()

@app.post("/detect_human_by_image")
async def detect_human_by_image_api(file: UploadFile = File(...)):
    image_bytes = await file.read()

    annotated_bytes, result_json = detect_human_by_image(image_bytes)

    return {
        "annotated_bytes": annotated_bytes,
        "result_json": result_json
    }