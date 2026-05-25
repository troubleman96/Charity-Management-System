"""
CharityOS — Development Settings
=================================
Extends base.py with development-specific configuration.
Uses SQLite and console email backend for easy local development.
"""
from .base import *  # noqa: F401,F403

# =============================================================================
# DEBUG MODE
# =============================================================================
DEBUG = True

# =============================================================================
# DATABASE — SQLite for development (no PostgreSQL required)
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# EMAIL — Print to console instead of sending real emails
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# STATIC FILES — No compression in development
# =============================================================================
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =============================================================================
# CELERY — Run tasks synchronously in development (no Redis needed)
# =============================================================================
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# =============================================================================
# LOGGING — Verbose output for development
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
