🚀 AI-Powered Code Review Assistant

An intelligent multi-agent code reviewer built with LangGraph and LangChain, enhanced with Retrieval-Augmented Generation (RAG) for context-aware best practices, and Model Context Protocol (MCP) for real-time IDE feedback.

This project analyzes code for style, security, performance, and documentation issues, then merges the results into concise, prioritized suggestions. Optimized prompts and retrieval pipelines achieved an ~85% suggestion acceptance rate during testing.

✨ Features

🧩 Multi-agent architecture (lint, security, performance, docs reviewers)

📚 RAG integration → retrieves coding best practices for context-aware reviews

⚡ Real-time IDE feedback via MCP server

📊 Aggregated suggestions ranked by severity and likelihood of acceptance

🛠️ CLI tool for batch reviewing repos and exporting JSON reports

🛠️ Tech Stack

Languages: Python

AI/LLM Tools: LangGraph, LangChain, Retrieval-Augmented Generation (RAG), MCP

Libraries: FAISS, Sentence-Transformers, Rich, Click

Platforms: OpenAI API, Hugging Face (optional), IBM Cloud (optional)

🚀 Getting Started

Clone repo & install dependencies

git clone https://github.com/yourusername/ai-code-review-assistant.git
cd ai-code-review-assistant
python -m venv .venv && source .venv/bin/activate
pip install -e .


Setup environment

cp .env.example .env   # fill in your API keys


Run CLI review

python -m src.cli review --path data/examples --topk 1


Run MCP server (IDE feedback)

python -m src.mcp_server

📊 Example Output
{
  "suggestions": [
    {
      "title": "Use parameterized SQL queries",
      "severity": "critical",
      "rationale": "Prevents SQL injection by avoiding string concatenation",
      "patch": "cur.execute('SELECT * FROM users WHERE name = ?', (user_input,))",
      "references": ["secure-coding.md"],
      "agent": "security"
    }
  ],
  "acceptance_likelihood": 0.85
}

📈 Results

Achieved ~85% suggestion acceptance rate in testing

Improved code quality, security, and performance with minimal developer overhead
