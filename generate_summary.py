from transformers import pipeline
from functools import lru_cache
import fitz  # PyMuPDF
from io import BytesIO
import re

# Lazy-load the summarizer only when needed and only once
@lru_cache(maxsize=1)
def get_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn", device=-1)

# Extract text from PDF using PyMuPDF (more accurate than pdfplumber)
def extract_text_with_fitz(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text

# Clean and normalize resume text for summarization
def clean_resume_text(text):
    # Remove emails and phone numbers
    text = re.sub(r'\S+@\S+|\+?\d[\d\s\-\(\)]{7,}', '', text)

    # Split lines and remove irrelevant or noisy ones
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    keywords_to_exclude = ['contact', 'email', 'linkedin', 'address', 'phone', 'resume', 'curriculum']
    cleaned_lines = [
        line for line in lines
        if not any(keyword in line.lower() for keyword in keywords_to_exclude)
    ]

    # Remove common bullet characters and merge to a single paragraph
    cleaned_lines = [re.sub(r'^[\-\•\*\–\●\▪]\s*', '', line) for line in cleaned_lines]
    cleaned_text = " ".join(cleaned_lines)

    # Truncate to 3000 characters if needed
    return cleaned_text[:3000]

# Generate a concise summary using the summarizer
def generate_concise_summary(text):
    summarizer = get_summarizer()

    # Optional prompt prefix to guide summarization
    prompt = "Summarize this resume focusing on experience, skills, and accomplishments:\n"
    input_text = prompt + text

    summary = summarizer(input_text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# Process the uploaded resume PDF and return the summary
def process_resume(pdf_file):
    pdf_file_stream = BytesIO(pdf_file)
    text = extract_text_with_fitz(pdf_file_stream)

    if not text.strip():
        return "No text found in the PDF."

    cleaned_text = clean_resume_text(text)

    if not cleaned_text.strip():
        return "Resume content couldn't be extracted properly."

    return generate_concise_summary(cleaned_text)
