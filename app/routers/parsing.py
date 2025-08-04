import os
import sys

tesseract_path = r"C:\Program Files\Tesseract-OCR"

if os.path.exists(tesseract_path) and tesseract_path not in os.environ['PATH']:
    os.environ['PATH'] = os.environ['PATH'] + os.pathsep + tesseract_path


import tempfile
from fastapi import Request, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from unstructured.partition.pdf import partition_pdf

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/parser-tool", response_class=HTMLResponse)
async def get_parser_tool(request: Request):
    """Serves the PDF Parser Inspector HTML page."""
    return templates.TemplateResponse(
        request=request, name="pdf-parser-inspector.html", context={}
    )


@router.post("/parse-document")
async def parse_document_endpoint(pdf_file: UploadFile = File(...)):
    """
    Accepts a PDF file and partitions it into structured elements
    using the 'unstructured' library with a high-resolution strategy.
    """
    try:
        # unstructured works best with file paths, so we save the upload to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await pdf_file.read())
            tmp_path = tmp.name

        # Use the hi_res strategy for OCR and layout detection
        elements = partition_pdf(tmp_path, strategy="hi_res")
        
        # Convert the element objects to a JSON-serializable format (dictionaries)
        response_data = [el.to_dict() for el in elements]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {e}")
    finally:
        # Clean up the temporary file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return response_data

