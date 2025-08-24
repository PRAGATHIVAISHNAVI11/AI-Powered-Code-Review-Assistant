from typing import Dict, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from .types import CodeSnippet, Suggestion, ReviewResult
from .rag import LocalRAG
from .agents import run_agent
from .prompts import AGGREGATOR_PROMPT
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
import os, json

class ReviewState(BaseModel):
    snippet: CodeSnippet
    rag_hits: List[dict] = []
    lint: List[Suggestion] = []
    security: List[Suggestion] = []
    performance: List[Suggestion] = []
    docs: List[Suggestion] = []
    merged: List[Suggestion] = []

def build_reviewer(corpus_dir: str, embed_model: str):
    rag = LocalRAG(corpus_dir, embed_model)
    rag.build()

    def node_rag(state: ReviewState):
        hits = rag.query(state.snippet.content, k=5)
        state.rag_hits = hits
        return state

    def node(kind: str):
        def f(state: ReviewState):
            suggestions = run_agent(kind, state.snippet, state.rag_hits)
            setattr(state, kind, suggestions)
            return state
        return f

    def node_aggregate(state: ReviewState):
        model = init_chat_model(model_name=os.getenv("OPENAI_MODEL","gpt-4o-mini"), model_provider="openai")
        combined = state.lint + state.security + state.performance + state.docs
        # keep raw for context
        prompt = AGGREGATOR_PROMPT + "\n\n" + json.dumps([s.model_dump() for s in combined])
        resp = model.invoke([SystemMessage(content="You are a precise aggregator of review suggestions."),
                             HumanMessage(content=prompt)])
        try:
            merged = json.loads(resp.content)
        except Exception:
            merged = [s.model_dump() for s in combined]

        # heuristic acceptance likelihood
        sev_map = {"critical": 0.9, "major": 0.75, "minor": 0.6, "info": 0.5}
        avg = sum(sev_map.get(x.get("severity","minor"), 0.6) for x in merged)/max(len(merged),1)

        state.merged = [Suggestion(**m) for m in merged]
        state._acceptance_likelihood = avg
        return state

    g = StateGraph(ReviewState)
    g.add_node("rag", node_rag)
    g.add_node("lint", node("lint"))
    g.add_node("security", node("security"))
    g.add_node("performance", node("performance"))
    g.add_node("docs", node("docs"))
    g.add_node("aggregate", node_aggregate)

    g.set_entry_point("rag")
    for nxt in ["lint","security","performance","docs"]:
        g.add_edge("rag", nxt)
        g.add_edge(nxt, "aggregate")
    g.add_edge("aggregate", END)

    return g.compile()
