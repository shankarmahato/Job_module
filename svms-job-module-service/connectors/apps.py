from django.apps import AppConfig

# setup logging
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger(__name__)

class ConfiguratorConfig(AppConfig):
    name = 'user'

