from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services
from app.services.ats_parser import ATSParser
from app.services.keyword_matcher import KeywordMatcher
from app.services.scorer import ResumeScorer
from app.services.ai_feedback import AIFeedbackGenerator

router = APIRouter()

# Initialize services
ats_parser = ATSParser()
keyword_matcher = KeywordMatcher()
scorer = ResumeScorer()
feedback_generator = AIFeedbackGenerator()

class AnalyzeRequest(BaseModel):
    resume_id: str
    extracted_text: str
    metadata: dict
    job_field: str
    user_id: str

@router.post("/analyze")
async def analyze_resume(request: AnalyzeRequest):
    """
    Analyze resume and generate scores, feedback, and suggestions
    """
    try:
        # Parse resume sections and extract information
        parsed_data = ats_parser.parse(request.extracted_text, request.metadata)
        
        # Match keywords with job field
        keyword_analysis = keyword_matcher.analyze(
            request.extracted_text,
            parsed_data['skills'],
            request.job_field
        )
        
        # Calculate scores
        ats_score = scorer.calculate_ats_score(parsed_data, keyword_analysis)
        job_fit_score = scorer.calculate_job_fit_score(parsed_data, keyword_analysis)
        
        # Generate radar chart data
        skills_radar = scorer.generate_skill_radar_data(keyword_analysis)
        
        # Calculate shortlist probability
        shortlist_prob = scorer.calculate_shortlist_probability(
            ats_score['total'],
            job_fit_score['total']
        )
        
        # Prepare analysis data for feedback generation
        analysis_data = {
            'scores': {
                'ats': ats_score,
                'job_fit': job_fit_score
            },
            'keyword_analysis': keyword_analysis,
            'parsed_data': parsed_data,
            'job_field': keyword_analysis['job_field'],
            'shortlist_probability': shortlist_prob
        }
        
        # Generate improvement suggestions
        suggestions = feedback_generator.generate_suggestions(analysis_data)
        
        # Generate detailed report
        detailed_report = feedback_generator.generate_detailed_report(analysis_data)
        
        # Prepare response
        response = {
            'analysis_id': request.resume_id,
            'user_id': request.user_id,
            'job_field': request.job_field,
            'scores': {
                'ats_score': ats_score['total'],
                'ats_grade': ats_score['grade'],
                'ats_breakdown': ats_score['breakdown'],
                'job_fit_score': job_fit_score['total'],
                'job_fit_grade': job_fit_score['grade'],
                'job_fit_breakdown': job_fit_score['breakdown']
            },
            'shortlist_probability': shortlist_prob,
            'keyword_analysis': {
                'match_percentage': keyword_analysis['keyword_match']['match_percentage'],
                'matched_keywords': keyword_analysis['keyword_match']['matched_keywords'],
                'missing_keywords': keyword_analysis['keyword_match']['missing_keywords'],
                'semantic_similarity': keyword_analysis['semantic_similarity'],
                'categorized_skills': keyword_analysis['categorized_skills']
            },
            'skills_radar_data': skills_radar,
            'parsed_sections': {
                'contact': parsed_data['contact'],
                'sections_found': list(parsed_data['sections'].keys()),
                'experience_count': len(parsed_data['experience']),
                'education_count': len(parsed_data['education'])
            },
            'formatting_analysis': parsed_data['formatting'],
            'suggestions': suggestions,
            'detailed_report': detailed_report,
            'status': 'completed'
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/job-fields")
async def get_job_fields():
    """
    Get list of available job fields
    """
    try:
        matcher = KeywordMatcher()
        job_fields = []
        
        for key, value in matcher.job_roles.items():
            job_fields.append({
                'value': key,
                'label': value['name'],
                'skills_count': len(value.get('core_skills', []))
            })
        
        return {'job_fields': job_fields}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job fields: {str(e)}")