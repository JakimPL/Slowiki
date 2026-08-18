import fcntl
import logging
import os
import signal
import socket
import subprocess
import sys
from collections.abc import Callable, Iterator
from contextlib import suppress
from http import HTTPStatus
from http.client import HTTPConnection, HTTPResponse
from json import dumps
from pathlib import Path
from time import monotonic, sleep
from typing import Any, Final, NamedTuple
from urllib.parse import quote

HOME: Final[Path] = Path(__file__).resolve().parents[1]
PACKAGES: Final[Path] = HOME / "src"
CONFIGURATION: Final[Path] = HOME / "config" / "config.yaml"
LOG: Final[Path] = HOME / "server.log"
LOCK: Final[Path] = HOME / "server.lock"
STANDING: Final[Path] = HOME / "server.state"
RESTART: Final[Path] = HOME / "tmp" / "restart.txt"

ADDRESS: Final[str] = "127.0.0.1"
PORT: Final[int] = 8532

CONNECT_PATIENCE: Final[float] = 10.0
STARTING_PATIENCE: Final[float] = 30.0
STOPPING_PATIENCE: Final[float] = 15.0
PROBE_PATIENCE: Final[float] = 0.5
BETWEEN_PROBES: Final[float] = 0.25
CHUNK: Final[int] = 65536

NEVER: Final[float] = 0.0
RECORDED: Final[int] = 2
NOT_OURS: Final[str] = "-"

REPORTED: Final[str] = "%(asctime)s %(levelname)s [%(process)d] passenger: %(message)s"
LISTENING: Final[int] = 0

HOP_BY_HOP: Final[frozenset[str]] = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    }
)

logging.basicConfig(
    level=logging.INFO,
    format=REPORTED,
    handlers=[logging.FileHandler(LOG, encoding="utf-8")],
)
LOGGER: Final[logging.Logger] = logging.getLogger("passenger")

Environ = dict[str, Any]
StartResponse = Callable[[str, list[tuple[str, str]]], object]


class Server(NamedTuple):
    process: int | None
    asked: float


def listening() -> bool:
    with socket.socket() as probe:
        probe.settimeout(PROBE_PATIENCE)
        return probe.connect_ex((ADDRESS, PORT)) == LISTENING


def asked_afresh() -> float:
    if not RESTART.is_file():
        return NEVER

    return RESTART.stat().st_mtime


def the_server_that_stands() -> Server | None:
    if not STANDING.is_file():
        return None

    stated = STANDING.read_text(encoding="utf-8").split()
    if len(stated) != RECORDED:
        return None

    try:
        return Server(None if stated[0] == NOT_OURS else int(stated[0]), float(stated[1]))
    except ValueError:
        return None


def remember(server: Server) -> None:
    process = NOT_OURS if server.process is None else str(server.process)
    STANDING.write_text(f"{process} {server.asked}\n", encoding="utf-8")


def out_of_date() -> bool:
    asked = asked_afresh()
    if asked == NEVER:
        return False

    standing = the_server_that_stands()
    return standing is None or standing.asked < asked


def stop_the_server(process: int) -> None:
    try:
        os.kill(process, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        LOGGER.error("process %d is not this account's to stop", process)
        return

    asked = monotonic()
    while monotonic() - asked < STOPPING_PATIENCE:
        if not listening():
            LOGGER.info(
                "the server on process %d stopped after %.1f seconds",
                process,
                monotonic() - asked,
            )
            return

        sleep(BETWEEN_PROBES)

    LOGGER.error(
        "process %d held the port through %.0f seconds, ending it outright",
        process,
        STOPPING_PATIENCE,
    )
    with suppress(ProcessLookupError):
        os.kill(process, signal.SIGKILL)


def retire_a_stale_server(asked: float) -> None:
    if asked == NEVER or not listening():
        return

    standing = the_server_that_stands()
    if standing is not None and standing.asked >= asked:
        return

    if standing is None or standing.process is None:
        LOGGER.error(
            "a server answers on %s:%d that this passenger did not start, so the restart asked for reaches"
            " nothing — `pkill -f wordtable.cli` stops it, and the next request starts the checkout as it"
            " now stands",
            ADDRESS,
            PORT,
        )
        remember(Server(None, asked))
        return

    LOGGER.info(
        "process %d was started before the last ask for a server afresh, stopping it",
        standing.process,
    )
    stop_the_server(standing.process)


def surroundings() -> dict[str, str]:
    stated = dict(os.environ)
    standing = [str(place) for place in (HOME, PACKAGES) if place.is_dir()]
    already = stated.get("PYTHONPATH")
    if already:
        standing.append(already)

    stated["PYTHONPATH"] = os.pathsep.join(standing)
    return stated


def start_the_server() -> None:
    with LOCK.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        asked = asked_afresh()
        retire_a_stale_server(asked)
        if listening():
            return

        if not CONFIGURATION.is_file():
            LOGGER.error(
                "no configuration stands at %s, which is the file the server is gathered from",
                CONFIGURATION,
            )
            return

        LOGGER.info("no server answers on %s:%d, starting one", ADDRESS, PORT)
        log = LOG.open("a", encoding="utf-8")
        try:
            started = subprocess.Popen(  # pylint: disable=consider-using-with
                [
                    sys.executable,
                    "-m",
                    "wordtable.cli",
                    "serve",
                    "--host",
                    ADDRESS,
                    "--port",
                    str(PORT),
                ],
                cwd=str(HOME),
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env=surroundings(),
            )
        finally:
            log.close()

        remember(Server(started.pid, asked))
        gathering = monotonic()
        while monotonic() - gathering < STARTING_PATIENCE:
            if listening():
                LOGGER.info(
                    "the server answers on process %d after %.1f seconds",
                    started.pid,
                    monotonic() - gathering,
                )
                return

            sleep(BETWEEN_PROBES)

        LOGGER.error(
            "no server answered inside %.0f seconds — read %s for what it said",
            STARTING_PATIENCE,
            LOG,
        )


def a_server_stands() -> None:
    RESTART.parent.mkdir(parents=True, exist_ok=True)
    if not listening() or out_of_date():
        start_the_server()


def headers_of(environ: Environ) -> list[tuple[str, str]]:
    carried = [
        (name.removeprefix("HTTP_").replace("_", "-").lower(), str(value))
        for name, value in environ.items()
        if name.startswith("HTTP_")
    ]
    for stated, header in (("CONTENT_TYPE", "content-type"), ("CONTENT_LENGTH", "content-length")):
        if environ.get(stated):
            carried.append((header, str(environ[stated])))

    return [(name, value) for name, value in carried if name not in HOP_BY_HOP]


def body_of(environ: Environ) -> bytes:
    stated = environ.get("CONTENT_LENGTH")
    length = int(stated) if stated else 0
    if length <= 0:
        return b""

    return bytes(environ["wsgi.input"].read(length))


def address_of(environ: Environ) -> str:
    path = quote(str(environ.get("PATH_INFO", "/")).encode("latin-1"))
    query = str(environ.get("QUERY_STRING", ""))
    return f"{path}?{query}" if query else path


def streaming(
    connection: HTTPConnection,
    answered: HTTPResponse,
) -> Iterator[bytes]:
    try:
        while chunk := answered.read1(CHUNK):
            yield chunk
    finally:
        connection.close()


def unreached(start_response: StartResponse, trouble: OSError) -> list[bytes]:
    LOGGER.error(
        "the server at %s:%d could not be reached: %s",
        ADDRESS,
        PORT,
        trouble,
    )
    body = dumps(
        {
            "detail": "The game server is not answering just now — try again in a moment",
            "code": "unreached",
        }
    ).encode("utf-8")
    start_response(
        f"{HTTPStatus.BAD_GATEWAY.value} {HTTPStatus.BAD_GATEWAY.phrase}",
        [("content-type", "application/json"), ("content-length", str(len(body)))],
    )
    return [body]


def application(
    environ: Environ,
    start_response: StartResponse,
) -> Iterator[bytes] | list[bytes]:
    a_server_stands()
    connection = HTTPConnection(ADDRESS, PORT, timeout=CONNECT_PATIENCE)
    try:
        connection.connect()
        if connection.sock is not None:
            connection.sock.settimeout(None)

        connection.request(
            str(environ.get("REQUEST_METHOD", "GET")),
            address_of(environ),
            body=body_of(environ),
            headers=dict(headers_of(environ)),
        )
        answered = connection.getresponse()
    except OSError as trouble:
        connection.close()
        return unreached(start_response, trouble)

    start_response(
        f"{answered.status} {answered.reason}",
        [
            (name.lower(), value)
            for name, value in answered.getheaders()
            if name.lower() not in HOP_BY_HOP
        ],
    )
    return streaming(connection, answered)
