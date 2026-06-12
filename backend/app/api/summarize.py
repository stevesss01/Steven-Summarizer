from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form
from fastapi import HTTPException

from app.services.pdf_service import (
    extract_text
)

from app.services.groq_service import (
    generate_summary
)

router = APIRouter()


@router.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    mode: str = Form(...)
):

    try:

        pdf_bytes = await file.read()

        text = extract_text(
            pdf_bytes
        )

        if not text.strip():

            raise HTTPException(
                status_code=400,
                detail="No text found in PDF"
            )

        summary = generate_summary(
            text,
            mode
        )

        return {
            "summary": summary
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )