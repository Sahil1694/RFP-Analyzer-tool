from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI(title="RFP Analysis API")

# Configure CORS to allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create storage directories if they don't exist
UPLOAD_DIR = "uploads"
RFP_DIR = os.path.join(UPLOAD_DIR, "rfp")
COMPANY_DATA_DIR = os.path.join(UPLOAD_DIR, "company_data")

os.makedirs(RFP_DIR, exist_ok=True)
os.makedirs(COMPANY_DATA_DIR, exist_ok=True)

class UploadResponse(BaseModel):
    rfp_id: Optional[str] = None
    company_data_id: Optional[str] = None
    message: str

@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(
    rfp_file: Optional[UploadFile] = File(None),
    company_data: Optional[UploadFile] = File(None),
):
    response_data = {
        "rfp_id": None,
        "company_data_id": None,
        "message": "Upload processed"
    }
    
    # Process RFP file if provided
    if rfp_file:
        # Validate file type
        if not rfp_file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(status_code=400, detail="RFP file must be PDF, DOC, or DOCX")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(rfp_file.filename)[1]
        new_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(RFP_DIR, new_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(rfp_file.file, buffer)
        
        response_data["rfp_id"] = file_id

    # Process company data file if provided
    if company_data:
        # Validate file type
        if not company_data.filename.lower().endswith(('.json', '.csv')):
            raise HTTPException(status_code=400, detail="Company data file must be JSON or CSV")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(company_data.filename)[1]
        new_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(COMPANY_DATA_DIR, new_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(company_data.file, buffer)
        
        response_data["company_data_id"] = file_id
    
    # If no files were uploaded
    if not rfp_file and not company_data:
        response_data["message"] = "No files were uploaded"
    
    return response_data

@app.get("/api/files/{file_id}")
async def get_file_status(file_id: str):
    # Check if file exists in either directory
    rfp_files = [f for f in os.listdir(RFP_DIR) if f.startswith(file_id)]
    company_files = [f for f in os.listdir(COMPANY_DATA_DIR) if f.startswith(file_id)]
    
    if rfp_files:
        return {"file_id": file_id, "type": "rfp", "filename": rfp_files[0], "status": "stored"}
    elif company_files:
        return {"file_id": file_id, "type": "company_data", "filename": company_files[0], "status": "stored"}
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Sample analysis endpoint that would process the uploaded RFP
@app.post("/api/analyze/{rfp_id}")
async def analyze_rfp(rfp_id: str):
    # Find the RFP file
    rfp_files = [f for f in os.listdir(RFP_DIR) if f.startswith(rfp_id)]
    
    if not rfp_files:
        raise HTTPException(status_code=404, detail="RFP file not found")
    
    # Here you would implement actual analysis logic
    
    return {
        "rfp_id": rfp_id,
        "analysis_status": "completed",
        "results": {
            "summary": "This is a placeholder for RFP analysis results",
            "key_requirements": ["Requirement 1", "Requirement 2"],
            "recommended_actions": ["Action 1", "Action 2"]
        }
    }

@app.get("/")
async def root():
    return {"message": "RFP Analysis API is running. Access /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)