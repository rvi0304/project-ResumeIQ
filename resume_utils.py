# resume_utils.py

from resume_comparison import search_resumes

def get_best_matching_resume(resume_texts, keyword, similarity_threshold=0.6):
    matched_resumes = search_resumes(resume_texts, keyword, similarity_threshold)
    if not matched_resumes:
        return None, matched_resumes
    # Find the resume with the highest similarity score
    best_resume = max(matched_resumes.items(), key=lambda x: x[1]["similarity_score"])[0]
    return best_resume, matched_resumes
