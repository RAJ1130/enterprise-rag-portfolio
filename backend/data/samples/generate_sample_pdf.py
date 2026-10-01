from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf():
    pdf_path = Path(__file__).resolve().parent / "Enterprise_Security_and_Access_Control_Policy.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0369a1'),
        spaceBefore=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Enterprise Security & Access Control Policy", title_style))
    story.append(Paragraph("<b>Policy ID:</b> SEC-POL-2026-09 | <b>Effective Date:</b> October 1, 2026 | <b>Classification:</b> Confidential Internal", body_style))
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. Purpose and Scope", h2_style))
    story.append(Paragraph(
        "This policy defines mandatory requirements for user identity authentication, credential hygiene, role-based access control (RBAC), and hardware security compliance across all corporate systems, production clusters, and cloud environments. Compliance is mandatory for all full-time employees, contractors, and third-party vendors.",
        body_style
    ))

    # Section 2
    story.append(Paragraph("2. Identity, Credential & Password Hygiene Standards", h2_style))
    story.append(Paragraph(
        "All corporate identities must adhere to strict zero-trust credential rules:",
        body_style
    ))

    pw_data = [
        ["Parameter", "Mandatory Requirement", "Enforcement Mechanism"],
        ["Minimum Length", "16 characters", "Okta Identity Engine filter"],
        ["Complexity", "Upper, lower, digits, special characters", "Automated regex check"],
        ["Rotation Schedule", "Mandatory every 90 days", "Automated account lockout warning"],
        ["MFA Requirement", "FIDO2 WebAuthn Hardware Key or Biometrics", "SMS/Voice call MFA prohibited"],
        ["Lockout Threshold", "5 consecutive failed attempts", "30-minute lock + Security alert"]
    ]
    t1 = Table(pw_data, colWidths=[120, 200, 160])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t1)
    story.append(Spacer(1, 14))

    # Section 3
    story.append(Paragraph("3. Zero Trust Remote Work & Network Perimeter", h2_style))
    story.append(Paragraph(
        "Direct SSH or RDP exposure to the public Internet is strictly forbidden. All engineers and staff accessing internal networks must route through the Corporate WireGuard VPN mesh with split-tunneling disabled for internal CIDR ranges (10.0.0.0/8). Session lifetimes are capped at 8 hours, requiring automated re-authentication.",
        body_style
    ))

    # Section 4
    story.append(Paragraph("4. Data Classification & Protection Tiers", h2_style))
    data_tiers = [
        ["Tier", "Classification", "Handling & Storage Requirements"],
        ["Tier 1", "Public", "No encryption required at rest. Freely sharable."],
        ["Tier 2", "Internal", "AES-256 encryption at rest. Internal staff access only."],
        ["Tier 3", "Confidential", "KMS Customer-Managed Keys (CMEK), audit logging required."],
        ["Tier 4", "Restricted / PII", "Field-level tokenization, strict RBAC, data masking on display."]
    ]
    t2 = Table(data_tiers, colWidths=[60, 110, 310])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0369a1')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 14))

    # Section 5
    story.append(Paragraph("5. Violation Penalties and Reporting", h2_style))
    story.append(Paragraph(
        "Suspected security compromises, lost hardware tokens, or anomalous access events must be reported to the Security Operations Center (SOC) at security-incident@enterprise.corp within 15 minutes of discovery. Willful non-compliance is grounds for immediate credential revocation and disciplinary review.",
        body_style
    ))

    doc.build(story)
    print(f"Generated sample PDF at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
