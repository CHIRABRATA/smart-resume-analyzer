from typing import Dict, List, Any
import os
from openai import OpenAI

class AIFeedbackGenerator:
    """Generate AI-powered improvement suggestions"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    def generate_suggestions(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        ats_score = analysis_data['scores']['ats']['total']
        job_fit_score = analysis_data['scores']['job_fit']['total']
        missing_keywords = analysis_data['keyword_analysis']['keyword_match']['missing_keywords']
        formatting_issues = analysis_data['parsed_data']['formatting']['issues']
        
        # ATS-specific suggestions
        if ats_score < 70:
            suggestions.append("🔧 **ATS Compatibility**: Your resume scored below 70% for ATS compatibility. Focus on simplifying formatting and using standard section headers.")
        
        for issue in formatting_issues:
            if "image" in issue.lower():
                suggestions.append("📷 **Remove Images**: ATS systems cannot read images. Replace with text descriptions.")
            elif "short" in issue.lower():
                suggestions.append("📝 **Expand Content**: Add more details about your experience and achievements (aim for 500-800 words).")
            elif "long" in issue.lower():
                suggestions.append("✂️ **Reduce Length**: Trim your resume to 1-2 pages by focusing on most relevant experiences.")
            elif "section" in issue.lower():
                suggestions.append(f"📋 **Add Sections**: {issue}")
        
        # Job fit suggestions
        if job_fit_score < 60:
            suggestions.append(f"🎯 **Improve Job Match**: Your resume matches only {job_fit_score:.0f}% with the target role. Add relevant keywords and experiences.")
        
        # Missing keywords
        if len(missing_keywords) > 0:
            top_missing = missing_keywords[:5]
            suggestions.append(f"🔑 **Add Keywords**: Include these high-value skills: {', '.join(top_missing)}")
        
        # Experience suggestions
        exp_score = analysis_data['scores']['job_fit']['breakdown']['experience_relevance']
        if exp_score < 70:
            suggestions.append("💼 **Quantify Achievements**: Add numbers and metrics to your experience bullets (e.g., 'Increased sales by 30%').")
        
        # Skills suggestions
        skills_score = analysis_data['scores']['job_fit']['breakdown']['skills_coverage']
        if skills_score < 60:
            suggestions.append("🛠️ **Expand Skills Section**: Add more technical skills relevant to your target role.")
        
        # Use AI for personalized feedback if available
        if self.client:
            ai_suggestions = self._generate_ai_suggestions(analysis_data)
            suggestions.extend(ai_suggestions)
        
        return suggestions[:8]  # Return top 8 suggestions
    
    def _generate_ai_suggestions(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate AI-powered personalized suggestions using GPT"""
        try:
            prompt = f"""
            Based on this resume analysis, provide 2-3 specific, actionable improvement suggestions:
            
            ATS Score: {analysis_data['scores']['ats']['total']}%
            Job Fit Score: {analysis_data['scores']['job_fit']['total']}%
            Target Role: {analysis_data['job_field']}
            Missing Keywords: {', '.join(analysis_data['keyword_analysis']['keyword_match']['missing_keywords'][:5])}
            
            Focus on practical improvements that will increase both ATS compatibility and job match percentage.
            Format each suggestion as: "emoji **Title**: Description"
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume consultant providing specific, actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_text = response.choices[0].message.content
            suggestions = [s.strip() for s in ai_text.split('\n') if s.strip()]
            return suggestions[:3]
        
        except Exception as e:
            print(f"AI suggestion generation failed: {str(e)}")
            return []
    
    def generate_detailed_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a detailed text report"""
        report = f"""
===========================================
        RESUME ANALYSIS REPORT
===========================================

TARGET ROLE: {analysis_data['job_field']}

SCORES:
-------
✓ ATS Compatibility: {analysis_data['scores']['ats']['total']}% (Grade: {analysis_data['scores']['ats']['grade']})
✓ Job Field Fit: {analysis_data['scores']['job_fit']['total']}% (Grade: {analysis_data['scores']['job_fit']['grade']})
✓ Shortlist Probability: {analysis_data['shortlist_probability']['probability']}

KEYWORD ANALYSIS:
-----------------
✓ Keywords Matched: {analysis_data['keyword_analysis']['keyword_match']['total_matched']}/{analysis_data['keyword_analysis']['keyword_match']['total_required']}
✓ Match Percentage: {analysis_data['keyword_analysis']['keyword_match']['match_percentage']}%
✓ Semantic Similarity: {analysis_data['keyword_analysis']['semantic_similarity']}%

TOP MISSING KEYWORDS:
{chr(10).join('  • ' + k for k in analysis_data['keyword_analysis']['keyword_match']['missing_keywords'][:10])}

SUGGESTIONS FOR IMPROVEMENT:
----------------------------
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(analysis_data['suggestions']))}

===========================================
        """
        return report.strip()





