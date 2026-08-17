import uvicorn

from wordserver.app import create_app
from wordtable.config import read_config
from wordtable.paths import RUN_CONFIG_FILE


def run() -> None:
    configuration = read_config(RUN_CONFIG_FILE)
    app = create_app()
    uvicorn.run(
        app,
        host=configuration.service.host,
        port=configuration.service.port,
    )
