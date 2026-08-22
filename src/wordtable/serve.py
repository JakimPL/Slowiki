import logging

import uvicorn

from wordserver.app import create_app
from wordtable.config import read_config
from wordtable.paths import RUN_CONFIG_FILE


def run(host: str | None, port: int | None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    configuration = read_config(RUN_CONFIG_FILE)
    app = create_app()
    uvicorn.run(
        app,
        host=configuration.service.host if host is None else host,
        port=configuration.service.port if port is None else port,
    )
