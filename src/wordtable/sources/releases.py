from typing import Final

from wordcore.models.base import BaseFrozen


class SourceRelease(BaseFrozen):
    stem: str
    suffix: str
    origin: str
    sha256: str

    @property
    def filename(self) -> str:
        return f"{self.stem}{self.suffix}"

    @property
    def url(self) -> str:
        return f"{self.origin}{self.filename}"


class DiscoveredRelease(BaseFrozen):
    stem: str
    url: str


SJP_INDEX: Final = "https://sjp.pl/sl/growy/"


SJP_RELEASE: Final = SourceRelease(
    stem="sjp-20260901",
    suffix=".zip",
    origin="https://sjp.pl/sl/growy/",
    sha256="43796ccf34a8ba9b6e965588b842721056b5a89cad4c8c38e057f838d4eaa6a5",
)

POLIMORF_RELEASE: Final = SourceRelease(
    stem="polimorf-20260726",
    suffix=".tab.gz",
    origin="https://download.sgjp.pl/morfeusz/20260726/",
    sha256="d0315301beb4820577c8e04c885044feb852a72c865ce62e5e0a1836344e078e",
)
