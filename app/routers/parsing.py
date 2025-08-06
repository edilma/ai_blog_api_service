import os
from fastapi import Request, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# Import the generic partition function
from unstructured.partition.auto import partition

# Ensure Tesseract is in the PATH on Windows
if os.name == 'nt': # Check if the OS is Windows
    tesseract_path = r"C:\Program Files\Tesseract-OCR"
    if os.path.exists(tesseract_path) and tesseract_path not in os.environ['PATH']:
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + tesseract_path

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/parser-tool", response_class=HTMLResponse)
async def get_parser_tool(request: Request):
    """Serves the Document Parser Inspector HTML page."""
    return templates.TemplateResponse(
        request=request, name="pdf-parser-inspector.html", context={}
    )

@router.post("/parse-document")
async def parse_document_endpoint(file: UploadFile = File(...)):
    """
    Accepts a file (PDF, DOCX, PPTX, etc.) and partitions it into structured elements.
    """
    strategy = "fast"
    # Use the hi_res strategy for PDFs to get the best results with OCR
    if file.content_type == "application/pdf":
        strategy = "hi_res"

    try:
        # The generic 'partition' function can handle the file in memory
        elements = partition(file=file.file, strategy=strategy, content_type=file.content_type)
        
        # Convert the element objects to a JSON-serializable format
        response_data = [el.to_dict() for el in elements]
        # --- DEBUGGING LINE ---
        print(f"--- Unstructured produced {len(response_data)} elements. ---")
        # -------------------------------

    except Exception as e:
        # Use repr(e) to get a more detailed error message
        raise HTTPException(status_code=500, detail=f"Failed to process file: {repr(e)}")

    return response_data