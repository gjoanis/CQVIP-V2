from app.models.project_phase import ProjectPhase
from app.repositories.base import BaseRepository


class PhaseRepository(BaseRepository[ProjectPhase]):
    model = ProjectPhase
