import logging
import logging.config
import os

configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging.conf')

logging.config.fileConfig(configPath)
logger = logging.getLogger('feiq')