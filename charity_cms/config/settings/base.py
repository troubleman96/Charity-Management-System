"""
CharityOS — Base Settings
=========================
Shared configuration used by both development and production environments.
Environment-specific overrides go in development.py or production.py.
"""
from pathlib import Path
import environ

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
# Build paths relative to the project root (charity_cms/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)
environ.Env.read_env(BASE_DIR / '.env')

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
INSTALLED_APPS = [
    # --- Django Built-in ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',            # Template filter for numbers (intcomma)

    # --- Third-Party ---
    'crispy_forms',                        # Form rendering helpers
    'django_htmx',                         # HTMX middleware & helpers
    'rest_framework',                      # REST API (for dashboard widgets)

    # --- Local Apps ---
    'apps.accounts.apps.AccountsConfig',
    'apps.donors.apps.DonorsConfig',
    'apps.beneficiaries.apps.BeneficiariesConfig',
    'apps.donations.apps.DonationsConfig',
    'apps.communications.apps.CommunicationsConfig',
    'apps.reports.apps.ReportsConfig',
    'apps.core.apps.CoreConfig',
]

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',           # HTMX request detection
]

# =============================================================================
# URL CONFIGURATION
# =============================================================================
ROOT_URLCONF = 'config.urls'

# =============================================================================
# TEMPLATES
# =============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],              # Project-level templates
        'APP_DIRS': True,                               # App-level templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Custom context processor — adds org name, unread counts, etc.
                'apps.core.context_processors.global_context',
            ],
        },
    },
]

# =============================================================================
# WSGI
# =============================================================================
WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'     # Tanzania timezone
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']     # Development static files
STATIC_ROOT = BASE_DIR / 'staticfiles'       # Collected static files (production)

# =============================================================================
# MEDIA FILES (User Uploads — photos, PDFs)
# =============================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# AUTHENTICATION
# =============================================================================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
SESSION_COOKIE_AGE = 1800                    # 30 minutes session timeout

# =============================================================================
# CRISPY FORMS
# =============================================================================
CRISPY_TEMPLATE_PACK = 'bootstrap4'          # Using custom CSS, this is fallback

# =============================================================================
# CELERY (Task Queue)
# =============================================================================
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Dar_es_Salaam'

# =============================================================================
# REST FRAMEWORK (for dashboard API widgets)
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# =============================================================================
# CHARITY-SPECIFIC SETTINGS
# =============================================================================
ORGANIZATION_NAME = env('ORG_NAME', default='Orphan Support Group')
ORGANIZATION_LOGO = 'images/org_logo.png'
LOW_FUNDS_THRESHOLD = env.float('LOW_FUNDS_THRESHOLD', default=100000.00)  # TZS
