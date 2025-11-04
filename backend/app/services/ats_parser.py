import re
import spacy
from typing import Dict, List, Any
import json

class ATSParser:
    """Parse resume sections and extract structured information"""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Section patterns
        self.section_patterns = {
            'contact': r'(email|phone|mobile|address|linkedin|github)',
            'summary': r'(summary|objective|profile|about)',
            'experience': r'(experience|employment|work history|professional experience)',
            'education': r'(education|academic|qualifications|degrees)',
            'skills': r'(skills|technical skills|competencies|expertise)',
            'projects': r'(projects|portfolio)',
            'certifications': r'(certifications|licenses|credentials)',
            'achievements': r'(achievements|awards|honors|accomplishments)'
        }
    
    def parse_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract resume sections"""
        lines = text.split('\n')
        sections = {}
        current_section = 'header'
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            section_found = None
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line_lower) and len(line.split()) <= 5:
                    section_found = section_name
                    break
            
            if section_found:
                # Save previous section
                if section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = section_found
                section_content = []
            else:
                section_content.append(line)
        
        # Save last section
        if section_content:
            sections[current_section] = '\n'.join(section_content).strip()
        
        return sections
    
    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""
        contact = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact['email'] = emails[0]
        
        # Phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact['linkedin'] = linkedin[0]
        
        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact['github'] = github[0]
        
        return contact
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using NLP"""
        doc = self.nlp(text.lower())
        
        # Common skill keywords
        skill_keywords = [
            'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'git', 'jira', 'agile', 'scrum', 'ci/cd', 'devops'
        ]
        
        found_skills = []
        for token in doc:
            if token.text in skill_keywords:
                found_skills.append(token.text)
        
        # Extract noun chunks that might be skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            if len(chunk_text.split()) <= 3:  # Skills are usually 1-3 words
                found_skills.append(chunk_text)
        
        return list(set(found_skills))
    
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience entries"""
        experiences = []
        
        # Pattern for years (2020-2023, 2020-Present, etc.)
        date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        
        lines = text.split('\n')
        current_exp = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_exp:
                    experiences.append(current_exp)
                    current_exp = {}
                continue
            
            # Check for date range
            date_match = re.search(date_pattern, line.lower())
            if date_match:
                current_exp['duration'] = date_match.group(0)
                current_exp['description'] = line
            elif current_exp:
                current_exp['description'] = current_exp.get('description', '') + ' ' + line
        
        if current_exp:
            experiences.append(current_exp)
        
        return experiences
    
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)',
            r'(undergraduate|graduate|postgraduate)'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            for pattern in degree_patterns:
                if re.search(pattern, line_lower):
                    education.append({
                        'degree': line.strip(),
                        'level': 'detected'
                    })
                    break
        
        return education
    
    def analyze_formatting(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Analyze resume formatting for ATS compatibility"""
        issues = []
        score = 100
        
        # Check for images (reduces ATS compatibility)
        if metadata.get('has_images', False):
            issues.append("Contains images - may not be ATS-friendly")
            score -= 10
        
        # Check length (1-2 pages ideal)
        word_count = len(text.split())
        if word_count < 300:
            issues.append("Resume too short (< 300 words)")
            score -= 15
        elif word_count > 1200:
            issues.append("Resume too long (> 1200 words, ~2 pages)")
            score -= 5
        
        # Check for standard sections
        sections = self.parse_sections(text)
        required_sections = ['experience', 'education', 'skills']
        missing_sections = [s for s in required_sections if s not in sections]
        
        if missing_sections:
            issues.append(f"Missing sections: {', '.join(missing_sections)}")
            score -= 10 * len(missing_sections)
        
        # Check contact info
        contact = self.extract_contact_info(text)
        if not contact.get('email'):
            issues.append("No email address found")
            score -= 10
        if not contact.get('phone'):
            issues.append("No phone number found")
            score -= 5
        
        return {
            'score': max(0, score),
            'issues': issues,
            'sections_found': list(sections.keys()),
            'word_count': word_count
        }
    
    def parse(self, text: str, metadata: Dict) -> Dict[str, Any]:
        """Main parsing method"""
        return {
            'sections': self.parse_sections(text),
            'contact': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'formatting': self.analyze_formatting(text, metadata)
        }