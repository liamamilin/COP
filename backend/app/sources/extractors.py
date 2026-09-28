import ipaddress
import re
import socket
from html.parser import HTMLParser
from io import BytesIO
from urllib.parse import urlparse

import httpx
from pypdf import PdfReader

from app.core.config import get_settings


class SourceExtractionError(ValueError):
    pass


def decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SourceExtractionError("Text encoding is not supported")
    text = text.replace("\x00", "").strip()
    if not text:
        raise SourceExtractionError("The source contains no readable text")
    return text


def extract_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise SourceExtractionError("The PDF could not be parsed") from exc
    if not text:
        raise SourceExtractionError("The PDF contains no extractable text")
    return text


class ReadableHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.suppressed = 0
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.suppressed += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self.suppressed:
            self.suppressed -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.suppressed:
            return
        value = data.strip()
        if not value:
            return
        self.parts.append(value)
        if self.in_title:
            self.title_parts.append(value)

    def result(self) -> tuple[str, str | None]:
        text = re.sub(r"[ \t]+", " ", " ".join(self.parts))
        text = re.sub(r"\s*\n\s*", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        title = " ".join(self.title_parts).strip() or None
        return text, title


def validate_remote_url(url: str, *, block_private_networks: bool = True) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise SourceExtractionError("Only public HTTP and HTTPS URLs are supported")
    if parsed.username or parsed.password:
        raise SourceExtractionError("URLs containing credentials are not supported")
    hostname = parsed.hostname.lower()
    if hostname == "localhost" or hostname.endswith((".localhost", ".local")):
        raise SourceExtractionError("Private, loopback, and local network URLs are blocked")
    try:
        literal_ip = ipaddress.ip_address(hostname)
    except ValueError:
        literal_ip = None
    if literal_ip is not None and not literal_ip.is_global:
        raise SourceExtractionError("Private, loopback, and local network URLs are blocked")
    if not block_private_networks:
        return
    try:
        addresses = socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise SourceExtractionError("The URL host could not be resolved") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise SourceExtractionError("Private, loopback, and local network URLs are blocked")


def extract_url(url: str, timeout: float) -> tuple[str, dict[str, str]]:
    strict_networks = get_settings().app_env not in {"development", "local", "test"}
    validate_remote_url(url, block_private_networks=strict_networks)
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url, headers={"User-Agent": "COP-Studio/0.1"})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise SourceExtractionError("The URL could not be fetched") from exc

    validate_remote_url(str(response.url), block_private_networks=strict_networks)
    content_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
    if len(response.content) > 10 * 1024 * 1024:
        raise SourceExtractionError("The remote source is larger than 10 MB")
    if content_type == "application/pdf":
        text = extract_pdf(response.content)
        title = None
    elif content_type in {"text/html", "application/xhtml+xml", ""}:
        parser = ReadableHTMLParser()
        parser.feed(response.text)
        text, title = parser.result()
    elif content_type.startswith("text/"):
        text = response.text.strip()
        title = None
    else:
        raise SourceExtractionError(f"Unsupported remote content type: {content_type}")
    if not text:
        raise SourceExtractionError("The URL contains no readable text")
    return text, {"final_url": str(response.url), "page_title": title or ""}
