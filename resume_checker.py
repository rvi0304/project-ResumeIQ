# resume_checker.py

import pdfplumber
from io import BytesIO
from generate_summary import process_resume

# Function to extract text from PDF
def extract_text_from_pdf(file_content):
    text = ""
    try:
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

def is_resume(text):
    if not text or len(text.strip().split()) < 50:
        return False

    text_lower = text.lower()

    must_have_sections = [
        "experience", "employment", "work history", "education", "degree",
        "skills", "technologies", "projects", "portfolio", "summary",
        "profile", "objective", "certifications", "courses"
    ]

    non_resume_words = [
        "invoice", "receipt", "bill to", "table of contents"
        # Removed: "report", "research paper"
    ]

    found_sections = [section for section in must_have_sections if section in text_lower]
    found_non_resume = [word for word in non_resume_words if word in text_lower]

    print(f"DEBUG: Found sections = {found_sections}")
    print(f"DEBUG: Found non-resume terms = {found_non_resume}")

    return len(found_sections) >= 2 and len(found_non_resume) == 0


# Optional testing block — only runs if script is run directly
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    def upload_and_check_resumes():
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(title="Select Resumes", filetypes=(("PDF files", "*.pdf"),))

        print("\nProcessing Uploaded Files:\n")
        for file_path in file_paths:
            print(f"Processing: {file_path}")
            with open(file_path, "rb") as file:
                content = file.read()
                text = extract_text_from_pdf(content)

                if is_resume(text):
                    print(f"✅ {file_path}: Valid Resume")
                    summary = process_resume(content)
                    print(f"📄 Summary:\n{summary}")
                else:
                    print(f"❌ {file_path}: Not a Resume. Try again!")
                print("-" * 60)

    upload_and_check_resumes()

