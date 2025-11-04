from typing import Dict, Any

class ResumeScorer:
    """Calculate ATS and Job Fit scores"""
    
    # Scoring weights
    WEIGHTS = {
        'ats': {
            'formatting': 0.20,
            'sections': 0.20,
            'readability': 0.20,
            'contact_info': 0.15,
            'length': 0.15,
            'keywords': 0.10
        },
        'job_fit': {
            'keyword_match': 0.40,
            'semantic_similarity': 0.20,
            'experience_relevance': 0.20,
            'education_fit': 0.10,
            'skills_coverage': 0.10
        }
    }
    
    def calculate_ats_score(self, parsed_data: Dict, keyword_analysis: Dict) -> Dict[str, Any]:
        """Calculate ATS compatibility score"""
        scores = {}
        
        # Formatting score
        formatting_score = parsed_data['formatting']['score']
        scores['formatting'] = formatting_score
        
        # Sections score
        required_sections = {'experience', 'education', 'skills', 'contact'}
        found_sections = set(parsed_data['sections'].keys())
        sections_score = (len(required_sections.intersection(found_sections)) / len(required_sections)) * 100
        scores['sections'] = sections_score
        
        # Readability score (based on word count)
        word_count = parsed_data['formatting']['word_count']
        if 300 <= word_count <= 800:
            readability_score = 100
        elif 800 < word_count <= 1200:
            readability_score = 90
        elif 200 <= word_count < 300:
            readability_score = 70
        else:
            readability_score = 50
        scores['readability'] = readability_score
        
        # Contact info score
        contact = parsed_data['contact']
        contact_score = 0
        if contact.get('email'): contact_score += 40
        if contact.get('phone'): contact_score += 30
        if contact.get('linkedin'): contact_score += 15
        if contact.get('github'): contact_score += 15
        scores['contact_info'] = contact_score
        
        # Length score
        if 300 <= word_count <= 1000:
            length_score = 100
        else:
            length_score = max(50, 100 - abs(word_count - 650) / 10)
        scores['length'] = length_score
        
        # Keyword presence score
        keyword_score = min(100, keyword_analysis['keyword_match']['match_percentage'] * 1.5)
        scores['keywords'] = keyword_score
        
        # Calculate weighted total
        total_score = sum(scores[key] * self.WEIGHTS['ats'][key] for key in scores.keys())
        
        return {
            'total': round(total_score, 2),
            'breakdown': scores,
            'grade': self._get_grade(total_score)
        }
    
    def calculate_job_fit_score(self, parsed_data: Dict, keyword_analysis: Dict) -> Dict[str, Any]:
        """Calculate job field fit score"""
        scores = {}
        
        # Keyword match score
        scores['keyword_match'] = keyword_analysis['keyword_match']['match_percentage']
        
        # Semantic similarity score
        scores['semantic_similarity'] = keyword_analysis['semantic_similarity']
        
        # Experience relevance (based on number of experiences and keywords)
        experience_count = len(parsed_data['experience'])
        if experience_count >= 3:
            experience_score = 100
        elif experience_count == 2:
            experience_score = 80
        elif experience_count == 1:
            experience_score = 60
        else:
            experience_score = 30
        scores['experience_relevance'] = experience_score
        
        # Education fit
        education_count = len(parsed_data['education'])
        education_score = min(100, education_count * 50)
        scores['education_fit'] = education_score
        
        # Skills coverage
        categorized = keyword_analysis['categorized_skills']
        core_skills_count = len(categorized['core_skills'])
        skills_coverage = min(100, core_skills_count * 10)
        scores['skills_coverage'] = skills_coverage
        
        # Calculate weighted total
        total_score = sum(scores[key] * self.WEIGHTS['job_fit'][key] for key in scores.keys())
        
        return {
            'total': round(total_score, 2),
            'breakdown': scores,
            'grade': self._get_grade(total_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 85:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 50:
            return 'C'
        elif score >= 30:
            return 'D'
        else:
            return 'F'
    
    def generate_skill_radar_data(self, keyword_analysis: Dict) -> list:
        """Generate data for skills radar chart"""
        categorized = keyword_analysis['categorized_skills']
        
        return [
            {'category': 'Core Skills', 'score': min(100, len(categorized['core_skills']) * 15)},
            {'category': 'Tools', 'score': min(100, len(categorized['tools']) * 15)},
            {'category': 'Frameworks', 'score': min(100, len(categorized['frameworks']) * 15)},
            {'category': 'Other Skills', 'score': min(100, len(categorized['other']) * 10)},
            {'category': 'Keywords', 'score': keyword_analysis['keyword_match']['match_percentage']},
        ]
    
    def calculate_shortlist_probability(self, ats_score: float, job_fit_score: float) -> Dict[str, Any]:
        """Calculate probability of getting shortlisted"""
        # Weighted average favoring job fit slightly more
        combined_score = (ats_score * 0.45) + (job_fit_score * 0.55)
        
        if combined_score >= 80:
            probability = "Very High (85-95%)"
            color = "#10b981"
        elif combined_score >= 65:
            probability = "High (70-85%)"
            color = "#3b82f6"
        elif combined_score >= 50:
            probability = "Moderate (50-70%)"
            color = "#f59e0b"
        elif combined_score >= 35:
            probability = "Low (30-50%)"
            color = "#ef4444"
        else:
            probability = "Very Low (< 30%)"
            color = "#991b1b"
        
        return {
            'pr,
            'combined_score': round(combined_score, 2),
            'color': color
        }