from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_resume_pdf():
    pdf_path = Path(__file__).resolve().parent / "Mummalar_Raj_Resume.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'NameTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=4
    )
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=10
    )
    section_title = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )
    bold_sub = ParagraphStyle(
        'BoldSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=2
    )

    story = []

    # Header
    story.append(Paragraph("Mummalar Raj A", title_style))
    story.append(Paragraph("Chennai, Tamil Nadu &nbsp;|&nbsp; +91 6382061572 &nbsp;|&nbsp; mummalarraj27@gmail.com &nbsp;|&nbsp; linkedin.com/in/mummalar-raj-515293297", contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=8))

    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_title))
    story.append(Paragraph(
        "A motivated frontend and full-stack developer fresher seeking an entry-level opportunity to apply skills in HTML, CSS, JavaScript, React.js, Python, and Django to design and develop responsive, scalable web applications. Successfully built projects including Cryptocurrency Tracker, Smart Health System, and an Enterprise RAG Knowledge Base. Eager to learn, grow, and contribute to dynamic software engineering teams.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_title))
    skills = [
        ["Programming Languages:", "JavaScript (ES6+), Python"],
        ["Frontend Technologies:", "HTML5, CSS3, JavaScript, React.js, Tailwind CSS, Bootstrap"],
        ["Backend Technologies:", "Django, Django REST Framework, FastAPI"],
        ["Databases & Vector Stores:", "MySQL, MongoDB, SQLite, Hybrid Vector Store (Dense + BM25)"],
        ["Full Stack Concepts:", "RESTful APIs, CRUD Operations, Authentication & Authorization, Client-Server Architecture, RAG Pipeline"],
        ["Tools & Platforms:", "Git, GitHub, Visual Studio Code, Postman, Vite, Docker"]
    ]
    t_skills = Table([[Paragraph(f"<b>{row[0]}</b>", body_style), Paragraph(row[1], body_style)] for row in skills], colWidths=[150, 380])
    t_skills.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_skills)
    story.append(Spacer(1, 4))

    # Experience
    story.append(Paragraph("INTERNSHIP EXPERIENCE", section_title))
    story.append(Paragraph("<b>BDreamz Global Solutions – Chennai</b> &nbsp;&nbsp;|&nbsp;&nbsp; <i>Feb 2026 – Present</i>", bold_sub))
    story.append(Paragraph("<b>Role: Full Stack Developer Intern</b>", body_style))
    story.append(Paragraph("• Built end-to-end web applications using HTML, CSS, JavaScript, React, and backend technologies during a 3-month practical internship.", body_style))
    story.append(Paragraph("• Designed responsive, accessible user interfaces, implemented server-side logic, and handled database integration.", body_style))
    story.append(Paragraph("• Delivered scalable, user-friendly solutions with robust client-server API workflows.", body_style))
    story.append(Spacer(1, 4))

    # Featured Projects
    story.append(Paragraph("FEATURED PROJECTS", section_title))
    
    # Project 1: Enterprise RAG
    story.append(Paragraph("<b>Enterprise RAG & Knowledge Base (Full-Stack AI Application)</b>", bold_sub))
    story.append(Paragraph("<i>Tech Stack: React.js, Tailwind CSS, FastAPI, Python, Vector DB (Cosine + BM25), Anti-Hallucination Guardrails</i>", body_style))
    story.append(Paragraph("• Built a zero-hallucination RAG knowledge base for enterprise documents (PDF, Markdown, CSV, TXT) with automatic page-level citations.", body_style))
    story.append(Paragraph("• Implemented hybrid retrieval using Reciprocal Rank Fusion (RRF) and 4-layer guardrails (Prompt Injection check, PII masking, Relevance Gate, and Faithfulness scoring).", body_style))
    story.append(Spacer(1, 3))

    # Project 2: Crypto Tracker
    story.append(Paragraph("<b>Crypto Tracker – Frontend Application</b>", bold_sub))
    story.append(Paragraph("<i>Tech Stack: HTML5, CSS3, JavaScript (ES6+), React.js</i>", body_style))
    story.append(Paragraph("• Developed a responsive cryptocurrency tracker with live pricing and historical trend tracking across days, months, and years.", body_style))
    story.append(Paragraph("• Integrated an AI chatbot assistant and built balance management features for income, expense, and real-time calculations.", body_style))
    story.append(Spacer(1, 3))

    # Project 3: Smart Health System
    story.append(Paragraph("<b>Smart Health System – Full Stack Application</b>", bold_sub))
    story.append(Paragraph("<i>Tech Stack: Python, Django, Django REST Framework, React.js</i>", body_style))
    story.append(Paragraph("• Built a full-stack task flow and health management system with modular Django REST Framework architecture.", body_style))
    story.append(Paragraph("• Created a responsive React SPA featuring reusable components, project boards, and team collaboration workflows.", body_style))
    story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION", section_title))
    story.append(Paragraph("<b>Mahendra College of Engineering, Salem, Tamil Nadu</b> &nbsp;&nbsp;|&nbsp;&nbsp; <i>Nov 2022 – May 2026</i>", bold_sub))
    story.append(Paragraph("B.Tech in Artificial Intelligence and Data Science &nbsp;|&nbsp; <b>CGPA: 7.4 / 10.0</b>", body_style))

    doc.build(story)
    print(f"Generated Mummalar Raj Resume PDF at: {pdf_path}")

if __name__ == "__main__":
    generate_resume_pdf()
