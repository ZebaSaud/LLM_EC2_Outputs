import requests
import subprocess
import os
from pathlib import Path


def get_files(directory):

    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files


# ==========================
# CONFIGURATION
# ==========================
OPENROUTER_API_KEY = "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"
MODEL_NAME = "deepseek/deepseek-coder"

IGNORE_DIRS = {"venv", ".git", "__pycache__", ".idea"}

# ==========================
# STEP 1: FIND ALL PYTHON FILES
# ==========================
def get_python_files(repo_dir):
    py_files = []
    for path in Path(repo_dir).rglob("*.py"):
        if not any(ignored in path.parts for ignored in IGNORE_DIRS):
            py_files.append(path)
    return py_files

# ==========================
# STEP 2: LLM ANALYSIS VIA OPENROUTER
# ==========================

def analyze_code_with_llm(code):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "HybridConsensusCodeReview"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": "You are a static analysis assistant for Python code."
            },
            {
                "role": "user",
                "content": (
                    "Review the following Python code and list findings strictly in bullet points.\n"
                    "Use these categories:\n"
                    "- Syntax errors\n"
                    "- Runtime risks\n"
                    "- Logical issues\n"
                    "- Code quality concerns\n\n"
                    f"{code[:12000]}"  # HARD SAFETY LIMIT
                )
            }
        ],
        "max_tokens": 500,
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"{response.status_code} {response.text}")

    return response.json()["choices"][0]["message"]["content"]


# ==========================
# STEP 3: RUN PIPELINE ON REPO
# ==========================
def analyze_repository(repo_dir, output_file="llm_code_review_web3.txt"):
    py_files = get_python_files(repo_dir)

    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"LLM Code Review Results\n")
        out.write(f"Repository: {repo_dir}\n")
        out.write("=" * 80 + "\n\n")

        for file_path in py_files:
            try:
                code = file_path.read_text(encoding="utf-8")
            except Exception as e:
                out.write(f"[ERROR] Could not read {file_path}: {e}\n\n")
                continue

            out.write(f"FILE: {file_path}\n")
            out.write("-" * 80 + "\n")

            try:
                analysis = analyze_code_with_llm(code)
                out.write(analysis + "\n\n")
            except Exception as e:
                out.write(f"[LLM ERROR] {e}\n\n")

    print(f"Analysis complete. Output saved to: {output_file}")

# ==========================
# STEP 4: ENTRY POINT
# ==========================


if __name__ == "__main__":
    repo_dir = "C:\\Users\\Administrator\\Desktop\\repos\\web3.py"
    #repo_path = get_files(repo_dir)
    analyze_repository(repo_dir)
