# pylint: disable=invalid-name

forwarded_allow_ips = "*"
worker_tmp_dir = "/dev/shm"

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {"handlers": ["default"], "level": "INFO"},
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "standard"}},
    "loggers": {
        "gunicorn.access": {"handlers": ["default"], "level": "INFO"},
        "gunicorn.error": {"handlers": ["default"], "level": "INFO"},
    },
}
