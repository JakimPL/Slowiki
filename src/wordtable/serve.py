import uvicorn

from wordserver.app import create_app
from wordtable.config import load_style, read_config
from wordtable.paths import CONFIG_DIR, PROJECT_ROOT


def run() -> None:
    configuration = read_config(CONFIG_DIR / "config.yaml")
    style = load_style(CONFIG_DIR, configuration.style)
    app = create_app(CONFIG_DIR, PROJECT_ROOT / "dictionaries", style)
    uvicorn.run(app, host=configuration.service.host, port=configuration.service.port)
