from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db  # noqa: F401  (re-exported for convenient `from app.api.deps import get_db`)
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc
    user = UserRepository(db).get(payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def verify_project_access(project_id: str, user: User, db: Session) -> None:
    """Raises 404 (not 403) if the project doesn't exist or isn't owned by
    `user`, so a foreign project_id is indistinguishable from a nonexistent
    one -- callers can't use this to probe which IDs exist in other accounts."""
    from app.repositories.project_repository import ProjectRepository

    project = ProjectRepository(db).get(project_id)
    if project is None or project.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")


def require_project_owner(
    project_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> str:
    """Dependency for routes where project_id is a path or query parameter --
    binds by parameter name the same way a route handler's own params would."""
    verify_project_access(project_id, current_user, db)
    return project_id


def require_fmea_owner(
    fmea_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> str:
    """Same idea as require_project_owner, but for routes nested under
    /fmea/{fmea_id}/... -- resolves the FMEA's project and checks that."""
    from app.repositories.fmea_repository import FmeaAnalysisRepository

    fmea = FmeaAnalysisRepository(db).get(fmea_id)
    if fmea is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "FMEA not found")
    verify_project_access(fmea.project_id, current_user, db)
    return fmea_id


def require_document_owner(
    document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
) -> str:
    """Same idea as require_project_owner, but for routes nested under
    /documents/{document_id}/... -- resolves the document's project and checks that."""
    from app.repositories.document_repository import DocumentRepository

    document = DocumentRepository(db).get(document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    verify_project_access(document.project_id, current_user, db)
    return document_id
