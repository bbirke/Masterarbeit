from pydantic import BaseModel
import configparser


class Config(object):

    def __init__(self, conf="./resources/config.ini"):
        self._cfg = configparser.ConfigParser()
        self._cfg.read(conf)

    def get_conf_value(self, section, prop=None):
        if section not in self._cfg:
            return None
        if not prop:
            return self._cfg[section]
        if prop not in self._cfg[section]:
            return None
        return self._cfg[section][prop]



class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "doc_seg_logger"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }
