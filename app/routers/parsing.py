import os
import json
import datetime
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

# --- Output directory ---
PROCESSED_DATA_DIR = "data/processed"
# Create the directory if it doesn't exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

@router.get("/parser-tool", response_class=HTMLResponse)
async def get_parser_tool(request: Request):
    """Serves the Document Parser Inspector HTML page."""
    return templates.TemplateResponse(
        request=request, name="pdf-parser-inspector.html", context={}
    )

@router.post("/parse-document")
async def parse_document_endpoint(file: UploadFile = File(...)):
    """
    Accepts a file (PDF, DOCX, PPTX, etc.),  partitions it into structured elements, 
    saves the raw elements to a unique JSON file,
    and returns the elements to the client.
    """
    # Create a dictionary of parameters to pass to the partition function
    partition_args = {
        "file": file.file,
        "content_type": file.content_type,
        "strategy": "fast" # Default strategy
    }

    strategy = "fast"
    # If the file is a PDF, use the advanced table extraction strategy
    if file.content_type == "application/pdf":
        partition_args["strategy"] = "hi_res"
        # This is the key parameter to activate advanced table parsing
        partition_args["pdf_infer_table_structure"] = True

    try:
        # --- STEP 1: Parse the document first ---
        #elements = partition(file=file.file, strategy=strategy, content_type=file.content_type)
        elements = partition(**partition_args)
        response_data = [el.to_dict() for el in elements]

        # --- STEP 2: Now create the unique filename ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        base_filename = os.path.splitext(file.filename)[0]
        output_filename = f"{timestamp}_{base_filename}.json"
        output_path = os.path.join(PROCESSED_DATA_DIR, output_filename)
  
        # --- STEP 3: Finally, save the data ---
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(response_data, f, ensure_ascii=False, indent=4)
        
        print(f"--- Successfully parsed and saved '{file.filename}' to '{output_path}' ---")

    except Exception as e:
        # Use repr(e) to get a more detailed error message
        raise HTTPException(status_code=500, detail=f"Failed to process file: {repr(e)}")

    return response_data