from app.ai.chat_assistant import ChatAssistant
from app.ai.requirement_extraction import RequirementExtraction
from app.ai.risk_analysis import RiskAnalysis


class AIService:
    """Dispatches to app/ai/* capabilities. Add one method per capability as you implement it."""

    def __init__(self):
        self.chat_assistant = ChatAssistant()
        self.requirement_extraction = RequirementExtraction()
        self.risk_analysis = RiskAnalysis()

    def chat(self, message: str, history: list[dict] | None = None) -> str:
        return self.chat_assistant.run(message, history=history or [])

    def extract_requirements(self, document_text: str) -> list[dict]:
        return self.requirement_extraction.run(document_text)

    def analyze_risk(self, requirement_text: str, context: str = "") -> dict:
        return self.risk_analysis.run(requirement_text, context=context)
