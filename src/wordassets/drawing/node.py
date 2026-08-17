from xml.sax.saxutils import escape, quoteattr

from wordcore.models.base import BaseFrozen


class Element(BaseFrozen):
    tag: str
    attributes: tuple[tuple[str, str], ...]
    children: tuple["Element", ...]
    text: str | None


def rendered(element: Element) -> str:
    attributes = "".join(f" {name}={quoteattr(value)}" for name, value in element.attributes)
    inner = _inner(element)
    if inner == "":
        return f"<{element.tag}{attributes}/>"

    return f"<{element.tag}{attributes}>{inner}</{element.tag}>"


def document(root: Element) -> str:
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{rendered(root)}\n'


def _inner(element: Element) -> str:
    parts = [escape(element.text)] if element.text is not None else []
    parts.extend(rendered(child) for child in element.children)
    return "".join(parts)
