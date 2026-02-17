import os
import base64
import json
import re
from typing import List, Optional, Literal
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env.local")
load_dotenv() # Fallback to system env or .env

app = FastAPI(title="ATS Resume Checker - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models (Matching Frontend) ---

class Header(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: Optional[str] = None
    website: Optional[str] = None

class ExperienceItem(BaseModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""
    achievements: List[str] = []

class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""
    gpa: Optional[str] = None

class Skills(BaseModel):
    technical: List[str] = []
    soft: List[str] = []
    languages: Optional[List[str]] = []

class CertificationItem(BaseModel):
    name: str = ""
    issuer: str = ""
    year: str = ""

class Sections(BaseModel):
    summary: Optional[str] = None
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    skills: Skills = Skills()
    certifications: Optional[List[CertificationItem]] = []

class ATSAnalysis(BaseModel):
    score: int = 0
    issues: List[str] = []
    recommendations: List[str] = []
    keyword_matches: List[str] = []
    missing_keywords: List[str] = []

class SuggestionCategory(BaseModel):
    category: str
    priority: Literal["Critical", "High", "Medium", "Low"]
    suggestions: List[str]
    impact: str

class ProSuggestionsSummary(BaseModel):
    total_categories: int
    total_suggestions: int
    potential_score_increase: int

class ProSuggestions(BaseModel):
    categories: List[SuggestionCategory]
    summary: ProSuggestionsSummary

class ResumeData(BaseModel):
    document_type: str = "resume"
    is_resume: bool = True
    message: Optional[str] = None
    header: Header = Header()
    sections: Sections = Sections()
    ats_analysis: ATSAnalysis = ATSAnalysis()
    pro_suggestions: Optional[ProSuggestions] = None
    raw_text: Optional[str] = None

class ProcessResponse(BaseModel):
    success: bool
    data: Optional[ResumeData] = None
    error: Optional[str] = None
    raw_text: Optional[str] = None

# --- Helper Functions ---

def simple_text_from_pdf(bytes_data: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
        reader = PdfReader(BytesIO(bytes_data))
        texts = []
        for p in reader.pages:
            texts.append(p.extract_text() or "")
        return "\n".join(texts)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def simple_text_from_docx(bytes_data: bytes) -> str:
    try:
        from io import BytesIO
        from docx import Document
        doc = Document(BytesIO(bytes_data))
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

# --- Routes ---

@app.post("/api/process-resume", response_model=ProcessResponse)
async def process_resume(file: UploadFile = File(...)):
    api_key = os.getenv("NEXT_PUBLIC_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
         return ProcessResponse(success=False, error="Server Error: Gemini API Key not configured.", data=None)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
         return ProcessResponse(success=False, error="Invalid file type. Please upload PDF or DOCX.", data=None)

    try:
        content = await file.read()
        
        # Extract text for fallback/context
        text_content = ""
        if file.content_type == "application/pdf":
            text_content = simple_text_from_pdf(content)
        else:
            text_content = simple_text_from_docx(content)

        # Prepare Gemini prompt
        # Note: We can send text directly or assume the model can handle it. 
        # For simplicity and robustness with the free tier, let's use the extracted text if possible, 
        # or base64 if it's an image-heavy PDF (but standard PyPDF2 implies text).
        
        prompt = """
        You are an expert ATS (Applicant Tracking System) simulator and resume branding consultant.
        Analyze the following resume text and structure it into a JSON format relative to the schema below.
        
        CRITICAL: Return ONLY valid JSON.
        
        Schema Structure:
        {
          "document_type": "resume" or "not_resume",
          "is_resume": true/false,
          "message": "Error message if not a resume",
          "header": { "name": "", "email": "", "phone": "", "location": "", "linkedin": "", "website": "" },
          "sections": {
            "summary": "Professional summary...",
            "experience": [ { "title": "", "company": "", "duration": "", "description": "", "achievements": [] } ],
            "education": [ { "degree": "", "institution": "", "year": "", "gpa": "" } ],
            "skills": { "technical": [], "soft": [], "languages": [] },
            "certifications": [ { "name": "", "issuer": "", "year": "" } ]
          },
          "ats_analysis": {
             "score": 0-100,
             "issues": ["list of critical issues"],
             "recommendations": ["list of actionable fixes"],
             "keyword_matches": ["found keywords"],
             "missing_keywords": ["important missing keywords"]
          },
          "pro_suggestions": {
            "categories": [
              {
                "category": "Header Optimization",
                "priority": "Critical",
                "suggestions": ["suggestion 1"],
                "impact": "High impact explanation"
              }
              // Add more categories: Experience, Skills, formatting...
            ],
            "summary": {
               "total_categories": 0,
               "total_suggestions": 0,
               "potential_score_increase": 0
            }
          }
        }
        
        Resume Content:
        """
        
        final_prompt = prompt + "\n\n" + text_content[:30000] # Truncate to avoid limits if huge

        response = model.generate_content(final_prompt)
        response_text = response.text
        
        # Clean markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        data_dict = json.loads(response_text)
        
        # Validate/Fill with defaults using Pydantic
        resume_data = ResumeData(**data_dict)
        resume_data.raw_text = text_content[:1000] # Preview

        return ProcessResponse(success=True, data=resume_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ProcessResponse(success=False, error=str(e), data=None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
