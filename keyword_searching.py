import pdfplumber
from io import BytesIO
import webbrowser
from sentence_transformers import SentenceTransformer, util

# Load the sentence transformer model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Extract text from PDF
def extract_text_from_pdf(file_content):
    text = ""
    try:
        with pdfplumber.open(BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

# Extract text from TXT
def extract_text_from_txt(file_content):
    try:
        return file_content.decode("utf-8")
    except Exception as e:
        print(f"Error extracting text from TXT: {e}")
        return ""

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

# Upload files and check if they are resumes
def upload_and_check_resumes():
    resumes = {}
    root = tk.Tk()
    root.withdraw()  # Hide the Tkinter root window

    file_paths = filedialog.askopenfilenames(
        title="Select Resumes",
        filetypes=(("PDF files", "*.pdf"), ("Text files", "*.txt"))
    )

    print("\n🔍 Processing Selected Files:\n")
    for file_path in file_paths:
        print(f"📄 Processing: {file_path}")
        with open(file_path, "rb") as file:
            content = file.read()
            text = ""
            if file_path.lower().endswith(".pdf"):
                text = extract_text_from_pdf(content)
            elif file_path.lower().endswith(".txt"):
                text = extract_text_from_txt(content)

            if is_resume(text):
                resumes[file_path] = text
                print(f"✅ Valid Resume: {file_path}")
            else:
                print(f"❌ Not a Resume: {file_path}")
        print("-" * 60)
    return resumes

# Search resumes for a given keyword using semantic similarity
def search_resumes(resumes, keyword, similarity_threshold=0.6):
    keyword_embedding = model.encode(keyword, convert_to_tensor=True)
    matching_resumes = {}

    for file_path, text in resumes.items():
        sentences = list(set(text.replace('\n', '. ').replace(',', '. ').split('.')))
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
        cosine_scores = util.cos_sim(keyword_embedding, sentence_embeddings)
        max_score = float(max(cosine_scores[0]))
        if max_score >= similarity_threshold:
            matching_resumes[file_path] = {
                "text": text,
                "similarity_score": round(max_score, 2)
            }

    return matching_resumes

# Compare matched resumes by similarity score
def compare_resumes(matching_resumes):
    if not matching_resumes:
        print("❌ No resumes to compare.")
        return

    print("\n📊 Resume Comparison (Based on Keyword Similarity):")
    sorted_resumes = sorted(matching_resumes.items(), key=lambda x: x[1]['similarity_score'], reverse=True)

    for rank, (file_path, info) in enumerate(sorted_resumes, start=1):
        print(f"{rank}. {file_path}")
        print(f"   🔹 Similarity Score: {info['similarity_score']}")
        # Optional: Show top 2-3 matching sentences
        print(f"   📌 Preview:\n   {get_top_matching_sentences(info['text'], search_keyword)}")
        print("-" * 60)

# Get top matching sentences from a resume for a keyword
def get_top_matching_sentences(text, keyword, top_k=3):
    sentences = list(set(text.replace('\n', '. ').replace(',', '. ').split('.')))
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    keyword_embedding = model.encode(keyword, convert_to_tensor=True)
    cosine_scores = util.cos_sim(keyword_embedding, sentence_embeddings)[0]

    top_indices = cosine_scores.argsort(descending=True)[:top_k]
    top_sentences = [sentences[i] for i in top_indices]
    return "\n   ".join(top_sentences)

if __name__ == "__main__":
    resumes = upload_and_check_resumes()
    if not resumes:
        print("\n⚠️ No valid resumes selected.")
        exit()

    search_keyword = input("\n🔍 Enter keyword to search in resumes (e.g., 'machine learning'): ")
    matched = search_resumes(resumes, search_keyword)

    print("\n📌 Matched Resumes:")
    if not matched:
        print("❌ No resumes matched the keyword.")
    else:
        compare_resumes(matched)  # ← ADD THIS

        for file_path, info in matched.items():
            if file_path.lower().endswith(".pdf"):
                try:
                    webbrowser.open_new_tab(f"file://{file_path}")
                    print(f"📂 Opened PDF: {file_path}")
                except Exception as e:
                    print(f"⚠️ Could not open file: {e}")
