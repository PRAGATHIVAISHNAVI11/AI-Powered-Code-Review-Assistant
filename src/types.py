from pydantic import BaseModel
from typing import List, Optional

class CodeSnippet(BaseModel):
    id: str
    path: str
    language: str = "python"
    code: str

class Suggestion(BaseModel):
    title: str
    rationale: str
    patch: Optional[str] = None
    severity: str = "minor"
    tags: List[str] = []
    references: List[str] = []
    agent: Optional[str] = None

class AgentResponse(BaseModel):
    agent_name: str
    reasoning: str
    response: str
    role: Optional[str] = "assistant"
    message: Optional[str] = None
