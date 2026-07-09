import os
import subprocess
import sys

from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage

DEFAULT_BASE_BRANCH = "main"
MAX_DIFF_CHARS = 12000


def run_git_command(args: list[str]) -> str:
    result = subprocess.run(args, capture_output=True, check=True, text=True)
    return result.stdout


def get_base_branch() -> str:
    return os.getenv("GITHUB_BASE_REF") or os.getenv("BASE_BRANCH") or DEFAULT_BASE_BRANCH


def get_diff() -> str:
    base_branch = get_base_branch()
    run_git_command(["git", "fetch", "origin", base_branch])
    return run_git_command(["git", "diff", f"origin/{base_branch}...HEAD"])


def truncate_diff(diff: str) -> str:
    if len(diff) <= MAX_DIFF_CHARS:
        return diff
    return diff[:MAX_DIFF_CHARS] + "\n\n[diff truncated]\n"


def create_review(diff: str) -> str:
    model_name = os.getenv("LLM_MODEL", "solar-pro3")
    llm = ChatUpstage(model=model_name)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior Python reviewer for a FastAPI/Streamlit AI agent project. "
                "Review only the provided git diff. Write concise Korean Markdown. "
                "Prioritize bugs, failing tests, security risks, and maintainability. "
                "Do not invent issues that are not visible in the diff.",
            ),
            (
                "human",
                "Review this diff:\n\n```diff\n{diff}\n```\n\n"
                "Format:\n"
                "## AI Review\n"
                "- Summary\n"
                "- Findings\n"
                "- Test Suggestions\n",
            ),
        ]
    )
    response = (prompt | llm).invoke({"diff": truncate_diff(diff)})
    return str(response.content)


def main() -> int:
    if not os.getenv("UPSTAGE_API_KEY"):
        print("UPSTAGE_API_KEY is not configured.")
        return 1

    try:
        diff = get_diff()
    except subprocess.CalledProcessError as exc:
        print(f"Failed to read git diff: {exc}", file=sys.stderr)
        return 1

    if not diff.strip():
        print("No diff found for AI review.")
        return 0

    try:
        print(create_review(diff))
    except Exception as exc:
        print(f"Failed to create AI review: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
