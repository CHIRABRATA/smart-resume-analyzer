from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import Dict, List, Any
import numpy as np

class KeywordMatcher:
    """Match resume keywords with job field requirements"""
    
    def __init__(self, job_roles_path: str = "app/data/job_roles.json"):
        with open(job_roles_path, 'r') as f:
            self.job_roles = json.load(f)
    
    def get_job_keywords(self, job_field: str) -> List[str]:
        """Get all keywords for a job field"""
        job_data = self.job_roles.get(job_field, {})
        
        keywords = []
        keywords.extend(job_data.get('core_skills', []))
        keywords.extend(job_data.get('tools', []))
        keywords.extend(job_data.get('frameworks', []))
        keywords.extend(job_data.get('keywords', []))
        
        return [k.lower() for k in keywords]
    
    def calculate_keyword_match(self, resume_text: str, job_field: str) -> Dict[str, Any]:
        """Calculate keyword match percentage"""
        job_keywords = self.get_job_keywords(job_field)
        resume_text_lower = resume_text.lower()
        
        matched_keywords = []
        missing_keywords = []
        
        for keyword in job_keywords:
            if keyword.lower() in resume_text_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        match_percentage = (len(matched_keywords) / len(job_keywords) * 100) if job_keywords else 0
        
        return {
            'match_percentage': round(match_percentage, 2),
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords[:10],  # Top 10 missing
            'total_required': len(job_keywords),
            'total_matched': len(matched_keywords)
        }
    
    def calculate_semantic_similarity(self, resume_text: str, job_field: str) -> float:
        """Calculate semantic similarity using TF-IDF"""
        job_keywords = self.get_job_keywords(job_field)
        job_description = ' '.join(job_keywords)
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        
        try:
            vectors = vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return round(similarity * 100, 2)
        except:
            return 0.0
    
    def categorize_skills(self, extracted_skills: List[str], job_field: str) -> Dict[str, List[str]]:
        """Categorize extracted skills by job requirements"""
        job_data = self.job_roles.get(job_field, {})
        
        categorized = {
            'core_skills': [],
            'tools': [],
            'frameworks': [],
            'other': []
        }
        
        core_skills_lower = [s.lower() for s in job_data.get('core_skills', [])]
        tools_lower = [t.lower() for t in job_data.get('tools', [])]
        frameworks_lower = [f.lower() for f in job_data.get('frameworks', [])]
        
        for skill in extracted_skills:
            skill_lower = skill.lower()
            if skill_lower in core_skills_lower:
                categorized['core_skills'].append(skill)
            elif skill_lower in tools_lower:
                categorized['tools'].append(skill)
            elif skill_lower in frameworks_lower:
                categorized['frameworks'].append(skill)
            else:
                categorized['other'].append(skill)
        
        return categorized
    
    def analyze(self, resume_text: str, extracted_skills: List[str], job_field: str) -> Dict[str, Any]:
        """Main analysis method"""
        keyword_match = self.calculate_keyword_match(resume_text, job_field)
        semantic_similarity = self.calculate_semantic_similarity(resume_text, job_field)
        categorized_skills = self.categorize_skills(extracted_skills, job_field)
        
        return {
            'keyword_match': keyword_match,
            'semantic_similarity': semantic_similarity,
            'categorized_skills': categorized_skills,
            'job_field': self.job_roles.get(job_field, {}).get('name', job_field)
        }