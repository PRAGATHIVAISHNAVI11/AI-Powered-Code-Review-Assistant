import os
from typing import List
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

from .types import CodeSnippet, Suggestion, AgentResponse
from .prompts import LINT_PROMPT, SECURITY_PROMPT, PERFORMANCE_PROMPT, DOCS_PROMPT, RAG_AUGMENT

load_dotenv()

INSTRUCTIONS = """Return JSON list of suggestions, each with:
title, rationale, patch (optional), severity (info|minor|major|critical), tags[], references[]. JSON only."""

def _call_llm(system_prompt: str, user_prompt: str) -> str:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = init_chat_model(model_name=model_name, model_provider="openai")
    msgs = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    resp = llm.invoke(msgs)
    return resp.content

def _build_user(snippet: CodeSnippet, rag_snippets: str) -> str:
    return f"""File: {snippet.path}
Language: {snippet.language}

CODE:

{snippet.code}

{rag_snippets}

{INSTRUCTIONS}
"""

def run_agent(kind: str, snippet: CodeSnippet, rag_snips: List[dict]) -> List[Suggestion]:
    if kind == "lint":
        system = LINT_PROMPT
    elif kind == "security":
        system = SECURITY_PROMPT
    elif kind == "performance":
        system = PERFORMANCE_PROMPT
    elif kind == "docs":
        system = DOCS_PROMPT
    else:
        raise ValueError("unknown agent")

    rag_text = ""
    if rag_snips:
        rag_text = RAG_AUGMENT.format(
            rag_snippets="\n\n".join([f"- ({s['path']}, score={s['score']:.2f})\n{s['doc']}" for s in rag_snips])
        )

    try:
        out = _call_llm(system, _build_user(snippet, rag_text))
        import json, re
        data = json.loads(re.sub(r"```json|```", "", out).strip())
    except Exception as e:
        return []

    suggestions = []
    for item in data:
        suggestions.append(Suggestion(
            title=item.get("title",""),
            rationale=item.get("rationale",""),
            patch=item.get("patch"),
            severity=item.get("severity","minor"),
            tags=item.get("tags",[]),
            references=item.get("references",[]),
            agent=kind
        ))
    return suggestions

def review_code(snippet: CodeSnippet, guidelines: List[str] = None) -> AgentResponse:
    try:
        suggestions = run_agent("lint", snippet, [])
        response_text = "\n".join([f"- {s.title}" for s in suggestions]) or "No suggestions."
        return AgentResponse(
            agent_name="CodeReviewer",
            reasoning="Suggestions generated successfully.",
            response=response_text,
            role="assistant",
            message=response_text
        )
    except Exception as e:
        return AgentResponse(
            agent_name="CodeReviewer",
            reasoning="Error while contacting OpenAI API.",
            response=f"Exception: {e}",
            role="assistant",
            message=f"Exception: {e}"
        )
