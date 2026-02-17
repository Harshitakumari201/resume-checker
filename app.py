import os
import re
from flask import Flask, render_template, request, jsonify
import PyPDF2
import docx
from collections import Counter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Common ATS keywords by category
ATS_KEYWORDS = {
    'technical_skills': [
        'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css', 
        'react', 'angular', 'vue', 'node.js', 'django', 'flask',
        'machine learning', 'data science', 'artificial intelligence',
        'aws', 'azure', 'cloud', 'docker', 'kubernetes', 'git'
    ],
    'soft_skills': [
        'leadership', 'communication', 'teamwork', 'problem solving',
        'analytical', 'critical thinking', 'time management', 'adaptability',
        'collaboration', 'creativity', 'attention to detail'
    ],
    'experience': [
        'managed', 'developed', 'designed', 'implemented', 'created',
        'led', 'coordinated', 'analyzed', 'improved', 'optimized',
        'achieved', 'delivered', 'built', 'established', 'executed'
    ],
    'education': [
        'bachelor', 'master', 'phd', 'degree', 'university', 'college',
        'certification', 'certified', 'graduate', 'diploma'
    ]
}

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return ""

def extract_text(file_path):
    """Extract text based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    return ""

def analyze_resume(text):
    """Analyze resume and calculate ATS score"""
    text_lower = text.lower()
    
    # Find matching keywords by category
    matches = {}
    total_matches = 0
    
    for category, keywords in ATS_KEYWORDS.items():
        category_matches = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                category_matches.append(keyword)
                total_matches += 1
        matches[category] = category_matches
    
    # Calculate ATS score (0-100)
    total_keywords = sum(len(keywords) for keywords in ATS_KEYWORDS.values())
    ats_score = min(100, int((total_matches / total_keywords) * 200))
    
    # Calculate category scores
    category_scores = {}
    for category, keywords in ATS_KEYWORDS.items():
        matched = len(matches[category])
        total = len(keywords)
        category_scores[category] = {
            'matched': matched,
            'total': total,
            'percentage': int((matched / total) * 100) if total > 0 else 0
        }
    
    # Word count and formatting analysis
    word_count = len(text.split())
    has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
    has_phone = bool(re.search(r'[\(]?\d{3}[\)]?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    
    return {
        'ats_score': ats_score,
        'matches': matches,
        'category_scores': category_scores,
        'total_matches': total_matches,
        'word_count': word_count,
        'has_email': has_email,
        'has_phone': has_phone
    }

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze uploaded resume"""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        # Extract and analyze
        text = extract_text(file_path)
        if not text:
            return jsonify({'error': 'Could not extract text from file'}), 400
        
        analysis = analyze_resume(text)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use environment variable to control debug mode (defaults to False for security)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
