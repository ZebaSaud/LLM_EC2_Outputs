import requests
import subprocess
from pathlib import Path

def clone_repo(repo_url, base_dir="repos"):
    base_dir = Path(base_dir)
    base_dir.mkdir(exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = base_dir / repo_name

    if not repo_path.exists():
        subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            check=True
        )

    return repo_path

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
def analyze_repository(repo_dir, output_file="llm_code_review_Brownie.txt"):
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
    GITHUB_REPO_URL = "https://github.com/eth-brownie/brownie"
    repo_path = clone_repo(GITHUB_REPO_URL)
    analyze_repository(repo_path)

