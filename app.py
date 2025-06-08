from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from generate_summary import process_resume
from resume_checker import is_resume, extract_text_from_pdf
from keyword_searching import search_resumes
import os

app = Flask(__name__)

# Folder to store uploaded PDFs
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store resumes globally
resumes_data = {}

# Route for the homepage
@app.route("/home")
def home():
    return render_template("home.html")

# Redirect "/" to the homepage
@app.route("/")
def redirect_to_home():
    return redirect(url_for("home"))

# Resume upload and analysis route
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    global resumes_data
    message = ""
    summaries = {}
    matched_resumes = {}
    uploaded_files = []
    best_resume = None

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        uploaded_files = request.files.getlist("resumes")

        for file in uploaded_files:
            if file and file.filename.endswith(".pdf"):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

                with open(file_path, "rb") as f:
                    content = f.read()
                    text = extract_text_from_pdf(content)

                if is_resume(text):
                    summary = process_resume(content)
                    resumes_data[file.filename] = {"text": text, "summary": summary}
                    summaries[file.filename] = summary
                else:
                    message += f"{file.filename} is not a valid resume.<br>"
                    os.remove(file_path)


        if keyword:
            resume_texts = {fname: data["text"] for fname, data in resumes_data.items()}
            matched_resumes = search_resumes(resume_texts, keyword)

            if matched_resumes:
                sorted_matches = sorted(matched_resumes.items(), key=lambda x: x[1]['similarity_score'], reverse=True)
                best_resume = sorted_matches[0][0]

                # ✅ Print comparison summary in command prompt
                print("\n📌 Resume Comparison Summary:")
                print("| Filename           | Similarity Score |")
                print("|--------------------|------------------|")
                for fname, info in sorted_matches:
                    print(f"| {fname:<18} | {info['similarity_score']:.2f}            |")
                print(f"\n🏆 Best Matching Resume: {best_resume}\n")


    existing_pdfs = list(resumes_data.keys())
    if not existing_pdfs and not message:
        message += "No valid resumes uploaded.<br>"

    return render_template(
        "index.html",
        message=message,
        summaries=summaries,
        matched_resumes=matched_resumes,
        best_resume=best_resume,
        uploaded_files=[file.filename for file in uploaded_files],
        existing_pdfs=existing_pdfs
    )

@app.route("/view_pdf/<filename>")
def view_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    all_summaries = "\n\n".join(
        f"{fname}: {data['summary']}" for fname, data in resumes_data.items()
    )
    return jsonify({"summary": all_summaries})

@app.route("/compare_resumes", methods=["POST"])
def compare_resumes():
    if not resumes_data:
        return jsonify({"bestResume": "No resumes uploaded."})

    data = request.get_json()
    keyword = data.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "Keyword is required for comparison."}), 400

    resume_texts = {fname: data["text"] for fname, data in resumes_data.items()}
    matched_resumes = search_resumes(resume_texts, keyword)

    if not matched_resumes:
        return jsonify({"bestResume": "No resumes matched the keyword."})

    sorted_resumes = sorted(matched_resumes.items(), key=lambda x: x[1]['similarity_score'], reverse=True)
    best_resume = sorted_resumes[0][0]

    comparison = {
        "bestResume": best_resume,
        "similarity_score": matched_resumes[best_resume]["similarity_score"],
        "allMatches": [
            {
                "filename": fname,
                "similarity": round(info["similarity_score"], 2)
            }
            for fname, info in sorted_resumes
        ]
    }

    return jsonify(comparison)

@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
