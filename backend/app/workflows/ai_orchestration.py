from sqlalchemy.orm import Session

from app.ai.gap_analysis import GapAnalysis
from app.ai.requirement_extraction import RequirementExtraction
from app.ai.risk_analysis import RiskAnalysis


class AIOrchestrationEngine:
    """Chains multiple AI capabilities into one pipeline, e.g. document -> requirements -> risks."""

    def __init__(self, db: Session):
        self.db = db
        self.extraction = RequirementExtraction()
        self.risk_analysis = RiskAnalysis()
        self.gap_analysis = GapAnalysis()

    def run_requirement_pipeline(self, document_text: str) -> dict:
        requirements = self.extraction.run(document_text)
        risks = [self.risk_analysis.run(r["description"]) for r in requirements]
        return {"requirements": requirements, "risks": risks}
