import os
import re
from flask import Flask, render_template, request, jsonify
import PyPDF2
import docx
import plotly.graph_objs as go
import plotly.utils
import json
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

def create_visualizations(analysis):
    """Create Plotly visualizations"""
    
    # ATS Score Gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=analysis['ats_score'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "ATS Score", 'font': {'size': 24}},
        delta={'reference': 70},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 70], 'color': '#fff4cc'},
                {'range': [70, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    # Category Scores Bar Chart
    categories = list(analysis['category_scores'].keys())
    percentages = [analysis['category_scores'][cat]['percentage'] for cat in categories]
    
    bar_chart = go.Figure(data=[
        go.Bar(
            x=categories,
            y=percentages,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
            text=percentages,
            textposition='auto',
        )
    ])
    bar_chart.update_layout(
        title='Keyword Match by Category',
        xaxis_title='Category',
        yaxis_title='Match Percentage (%)',
        yaxis=dict(range=[0, 100])
    )
    
    # Keyword Distribution Pie Chart
    matched_counts = [len(analysis['matches'][cat]) for cat in categories]
    
    pie_chart = go.Figure(data=[go.Pie(
        labels=categories,
        values=matched_counts,
        hole=.3
    )])
    pie_chart.update_layout(title='Matched Keywords Distribution')
    
    return {
        'gauge': json.dumps(gauge, cls=plotly.utils.PlotlyJSONEncoder),
        'bar_chart': json.dumps(bar_chart, cls=plotly.utils.PlotlyJSONEncoder),
        'pie_chart': json.dumps(pie_chart, cls=plotly.utils.PlotlyJSONEncoder)
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
    app.run(debug=True, host='0.0.0.0', port=5000)
