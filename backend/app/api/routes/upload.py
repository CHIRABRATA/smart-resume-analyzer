from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.text_extraction import TextExtractor

router = APIRouter()
text_extractor = TextExtractor()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    job_field: str = Form(...),
    user_id: str = Form(...)
):
    """
    Upload and process a resume file
    """
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'application/msword', 
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
                                
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOC/DOCX allowed.")
        
        # Validate file size
        contents = await file.read()
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Extract text
        extracted_data = text_extractor.extract(file_path, file_extension)
        
        # Create response
        response_data = {
            'resume_id': str(uuid.uuid4()),
            'file_name': file.filename,
            'file_path': file_path,
            'job_field': job_field,
            'user_id': user_id,
            'extracted_text': extracted_data['text'],
            'metadata': extracted_data['metadata'],
            'word_count': extracted_data['word_count'],
            'upload_time': datetime.now().isoformat(),
            'status': 'success'
        }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")