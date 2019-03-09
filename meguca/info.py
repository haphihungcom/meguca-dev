"""Advanced configurations.
"""


# Directory to find plugin description files
PLUGIN_DIR_PATH = 'meguca/plugins'

# Plugin description file extension
PLUGIN_DESC_EXT = 'plugin'

# Path to general configuration file
GENERAL_CONFIG_PATH = 'meguca/config/general_config.toml'

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,

    'formatters': {
        'MegucaFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s : %(message)s'
        }
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'MegucaFormatter',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'MegucaFormatter',
            'filename': 'meguca.log',
            'maxBytes': 20000000,
            'backupCount': 5
        }
    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}
