import os
import subprocess
from pathlib import Path

REPO_PATH = Path(r"C:\\Users\\Administrator\\Desktop\\repos\\web3.py")   # CHANGE THIS
OUTPUT_FILE = "static_analysis_result_web3.txt"


def get_python_files(repo_path):
    py_files = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def run_tool(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"[ERROR] {e}"


def main():
    py_files = get_python_files(REPO_PATH)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"Static Analysis Results\n")
        out.write(f"Repository: {REPO_PATH}\n")
        out.write("=" * 80 + "\n\n")

        for file in py_files:
            out.write(f"FILE: {file}\n")
            out.write("-" * 80 + "\n")

            # pylint
            pylint_output = run_tool(["pylint", file, "--score=n"])
            out.write("[PYLINT]\n")
            out.write(pylint_output.strip() + "\n\n")

            # mypy.


            mypy_output = run_tool(["mypy", file, "--ignore-missing-imports"])
            out.write("[MYPY]\n")
            out.write(mypy_output.strip() + "\n\n")

            # bandit
            bandit_output = run_tool(["bandit", "-q", "-r", file])
            out.write("[BANDIT]\n")
            out.write(bandit_output.strip() + "\n\n")

            out.write("=" * 80 + "\n\n")

    print(f"Analysis complete. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
