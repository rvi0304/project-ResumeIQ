# # resume_comparison.py

import webbrowser
from keyword_searching import upload_and_check_resumes, search_resumes

def open_pdf(filepath):
    try:
        webbrowser.open_new_tab(f"file://{filepath}")
        print(f"📂 Opened PDF: {filepath}")
    except Exception as e:
        print(f"⚠️ Could not open file: {e}")

def display_matched_resumes(matched_resumes):
    print("\n📌 Matched Resumes:")
    for file_path, info in matched_resumes.items():
        print(f"✅ {file_path} (Similarity: {info['similarity_score']:.2f})")
        if file_path.lower().endswith(".pdf"):
            open_pdf(file_path)

def get_best_matching_resume(matched_resumes):
    return max(matched_resumes, key=lambda f: matched_resumes[f]['similarity_score'])

def compare_resumes_by_keyword(keyword, similarity_threshold=0.6):
    print("\n🔄 Uploading and checking resumes...")
    resumes = upload_and_check_resumes()

    if not resumes:
        print("⚠️ No valid resumes found.")
        return None, {}

    print(f"\n🔍 Searching resumes for keyword: '{keyword}'")
    matched = search_resumes(resumes, keyword, similarity_threshold)

    if not matched:
        print("❌ No resumes matched the keyword.")
        return None, {}

    display_matched_resumes(matched)

    best_file = get_best_matching_resume(matched)
    print(f"\n🏆 Best Matching Resume:\n{best_file} (Similarity: {matched[best_file]['similarity_score']:.2f})")

    open_pdf(best_file)
    return best_file, matched

if __name__ == "__main__":
    keyword = input("Enter keyword to compare resumes: ")
    compare_resumes_by_keyword(keyword)
