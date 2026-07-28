from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Section:
    heading: str
    text: str


@dataclass
class ParseResult:
    raw_text: str
    sections: list[Section] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        raise NotImplementedError
