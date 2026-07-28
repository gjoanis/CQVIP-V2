class CQVIPError(Exception):
    """Base class for application errors."""


class NotFoundError(CQVIPError):
    def __init__(self, entity: str, identifier):
        super().__init__(f"{entity} not found: {identifier}")
        self.entity = entity
        self.identifier = identifier


class ValidationError(CQVIPError):
    pass


class PermissionDeniedError(CQVIPError):
    pass


class IntegrationError(CQVIPError):
    """Raised by app/integrations/* adapters when an external call fails."""
