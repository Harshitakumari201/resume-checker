# 📄 Resume ATS Checker with Visualization

A powerful web application that analyzes resumes and calculates ATS (Applicant Tracking System) scores with beautiful, interactive visualizations.

## 🌟 Features

- **ATS Score Calculator**: Get instant feedback on how well your resume will perform with ATS systems
- **Interactive Visualizations**: 
  - Gauge chart showing your overall ATS score
  - Bar chart displaying keyword matches by category
  - Pie chart showing keyword distribution
- **Keyword Analysis**: Identifies matched keywords across multiple categories:
  - Technical Skills (Python, JavaScript, Cloud, etc.)
  - Soft Skills (Leadership, Communication, etc.)
  - Experience Keywords (Managed, Developed, etc.)
  - Education Terms
- **Smart Recommendations**: Get actionable suggestions to improve your resume
- **Multi-format Support**: Upload PDF, DOCX, or TXT files
- **Beautiful UI**: Modern, responsive design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Harshitakumari201/resume-checker.git
cd resume-checker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask server:
```bash
python app.py
```

For development with debug mode enabled:
```bash
FLASK_DEBUG=true python app.py
```

**Note**: Debug mode is disabled by default for security. Only enable it during development.
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload your resume (PDF, DOCX, or TXT format)

4. Click "Analyze Resume" to get your results

## 📊 Understanding Your Results

### ATS Score (0-100)
- **0-50**: Low score - needs significant improvement
- **50-70**: Moderate score - add more relevant keywords
- **70-100**: Good score - well-optimized for ATS

### Visualizations

1. **ATS Score Gauge**: Visual representation of your overall score with color-coded zones
2. **Category Match Chart**: Shows how well you match keywords in each category
3. **Keyword Distribution**: Pie chart showing the spread of matched keywords

### Recommendations

The system provides personalized recommendations based on your analysis:
- Keyword suggestions for each category
- Contact information completeness
- Resume length guidance
- Category-specific improvements

## 📁 Project Structure

```
resume-checker/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore file
├── templates/
│   └── index.html            # Main web interface
├── static/
│   └── css/
│       └── style.css         # Styling
├── examples/
│   ├── sample_resume_high_score.txt
│   └── sample_resume_low_score.txt
└── README.md                 # This file
```

## 🎯 How It Works

1. **Upload**: User uploads a resume in supported format
2. **Text Extraction**: System extracts text from the file
3. **Keyword Matching**: Analyzes text against comprehensive keyword database
4. **Score Calculation**: Computes ATS score based on matched keywords
5. **Visualization**: Creates interactive charts using Plotly
6. **Recommendations**: Generates personalized improvement suggestions

## 🔧 Technologies Used

- **Backend**: Flask (Python web framework)
- **Text Extraction**: PyPDF2, python-docx
- **Visualizations**: Plotly
- **Frontend**: HTML5, CSS3, JavaScript
- **File Handling**: Multi-format support (PDF, DOCX, TXT)

## 📝 Example Usage

Try the example resumes in the `examples/` folder:
- `sample_resume_high_score.txt`: Well-optimized resume (expected score: 70+)
- `sample_resume_low_score.txt`: Basic resume needing improvement (expected score: <30)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source and available under the MIT License.

## 👩‍💻 Author

Harshita Kumari

## 🙏 Acknowledgments

- Built with Flask and Plotly
- Inspired by the need for better ATS optimization tools
- Thanks to all contributors and users

---

**Note**: This tool provides estimates based on keyword matching. Actual ATS systems may use different algorithms. Always tailor your resume to specific job descriptions for best results.
