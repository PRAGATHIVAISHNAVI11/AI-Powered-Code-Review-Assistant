import os
import argparse
from dotenv import load_dotenv

from .types import CodeSnippet
from .agents import review_code

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Run AI Code Review Assistant")
    parser.add_argument("--path", type=str, required=True, help="Path to code file")
    parser.add_argument("--guidelines", nargs="*", help="Optional guidelines for review")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"❌ File not found: {args.path}")
        return

    with open(args.path, "r", encoding="utf-8") as f:
        code_content = f.read()

    snippet = CodeSnippet(id=args.path, path=args.path, code=code_content)

    result = review_code(snippet, args.guidelines)

    print("\n=== AI Code Review Result ===")
    print(f"👩‍💻 Agent: {result.agent_name}")
    print(f"📖 Reasoning: {result.reasoning}")
    print(f"✅ Suggestions:\n{result.response}")
    print("=============================\n")

if __name__ == "__main__":
    main()
