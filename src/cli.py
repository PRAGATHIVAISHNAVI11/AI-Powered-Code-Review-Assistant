import os, glob, click, json
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from .types import CodeSnippet, ReviewResult
from .build_graph import build_reviewer

console = Console()

LANG_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".go": "go", ".cs": "csharp", ".cpp": "cpp"
}

def detect_lang(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return LANG_MAP.get(ext, "text")

@click.group()
def cli():
    pass

@cli.command()
@click.option("--path", type=click.Path(exists=True, file_okay=True, dir_okay=True), required=True,
              help="File or directory to review")
@click.option("--globpat", default="**/*.*", help="Glob for directory mode")
@click.option("--topk", default=1, help="Max files to sample (dir mode)")
def review(path, globpat, topk):
    load_dotenv()
    graph = build_reviewer("data/corpus", os.getenv("EMBED_MODEL","sentence-transformers/all-MiniLM-L6-v2"))
    files = [path]
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, globpat), recursive=True)[:topk]

    for fp in files:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        snippet = CodeSnippet(path=fp, language=detect_lang(fp), content=content)
        state = graph.invoke({"snippet": snippet})
        suggestions = state["merged"]
        likelihood = state.get("_acceptance_likelihood", 0.6)

        console.rule(f"[bold]Review: {fp}")
        table = Table("Severity","Title","Agent","Refs")
        for s in suggestions:
            refs = ", ".join(s.references) if s.references else "-"
            table.add_row(s.severity, s.title, s.agent, refs)
        console.print(table)
        console.print(f"[bold]Acceptance Likelihood:[/bold] {likelihood:.2f}")

        out = ReviewResult(file=fp, suggestions=suggestions, acceptance_likelihood=likelihood)
        os.makedirs("out", exist_ok=True)
        with open(os.path.join("out", os.path.basename(fp) + ".review.json"), "w", encoding="utf-8") as w:
            w.write(out.model_dump_json(indent=2))

if __name__ == "__main__":
    cli()
