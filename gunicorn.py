# pylint: disable=invalid-name

forwarded_allow_ips = "*"
worker_tmp_dir = "/dev/shm"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

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
