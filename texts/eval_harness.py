import json, difflib
from pathlib import Path

def diff_acceptance(before: str, after: str, suggestions: list[dict]) -> float:
    """
    Heuristic: if patches suggested are similar to applied changes, count as accepted.
    (For MVP demo only.)
    """
    d = "\n".join(difflib.unified_diff(before.splitlines(), after.splitlines()))
    hits = 0
    for s in suggestions:
        patch = (s.get("patch") or "").strip()
        if patch and len(patch) > 10:
            # crude similarity
            sm = difflib.SequenceMatcher(None, d, patch).ratio()
            if sm > 0.25:
                hits += 1
    return hits / max(len([s for s in suggestions if s.get("patch")]), 1)

def main():
    from src.types import CodeSnippet
    from src.build_graph import build_reviewer
    import os
    graph = build_reviewer("data/corpus", os.getenv("EMBED_MODEL","sentence-transformers/all-MiniLM-L6-v2"))

    rows = [json.loads(l) for l in Path("tests/fixtures/sample_before_after.jsonl").read_text().splitlines()]
    ratios = []
    for r in rows:
        snippet = CodeSnippet(path="<mem>", language="python", content=r["before"])
        st = graph.invoke({"snippet": snippet})
        suggestions = [s.model_dump() for s in st["merged"]]
        ratios.append(diff_acceptance(r["before"], r["after"], suggestions))
    print(f"Estimated suggestion acceptance rate (demo): {sum(ratios)/len(ratios):.2f}")

if __name__ == "__main__":
    main()
