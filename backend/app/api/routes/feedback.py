from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class FeedbackRequest(BaseModel):
    analysis_id: str
    user_id: str

@router.get("/feedback/{analysis_id}")
async def get_feedback(analysis_id: str):
    """
    Get detailed feedback for an analysis
    """
    try:
        # In a real application, this would fetch from database
        # For now, return a structured feedback template
        
        feedback = {
            'analysis_id': analysis_id,
            'feedback_sections': [
                {
                    'title': 'ATS Optimization',
                    'items': [
                        'Use standard section headers (Experience, Education, Skills)',
                        'Avoid tables, images, and complex formatting',
                        'Use standard fonts (Arial, Calibri, Times New Roman)',
                        'Save as .docx or PDF format',
                        'Keep file size under 1MB'
                    ]
                },
                {
                    'title': 'Content Improvement',
                    'items': [
                        'Start bullet points with action verbs',
                        'Quantify achievements with numbers',
                        'Tailor content to job description',
                        'Include relevant keywords naturally',
                        'Keep descriptions concise and impactful'
                    ]
                },
                {
                    'title': 'Keyword Strategy',
                    'items': [
                        'Research job postings in your field',
                        'Include both hard and soft skills',
                        'Use industry-specific terminology',
                        'Match keywords from job descriptions',
                        'Avoid keyword stuffing'
                    ]
                }
            ],
            'additional_resources': [
                {
                    'title': 'Resume Templates',
                    'url': 'https://example.com/templates',
                    'description': 'ATS-friendly resume templates'
                },
                {
                    'title': 'Action Verbs Guide',
                    'url': 'https://example.com/action-verbs',
                    'description': 'Powerful action verbs for resumes'
                }
            ]
        }
        
        return feedback
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@router.post("/save-feedback")
async def save_user_feedback(
    analysis_id: str,
    rating: int,
    comments: Optional[str] = None
):
    """
    Save user feedback about the analysis
    """
    try:
        # In production, save to database
        feedback_data = {
            'analysis_id': analysis_id,
            'rating': rating,
            'comments': comments,
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'status': 'success',
            'message': 'Feedback saved successfully',
            'data': feedback_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")