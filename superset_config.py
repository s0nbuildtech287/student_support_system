import os

SECRET_KEY = "Jx8kF2!9vQmP@eR7#WzYB4A6Hn0sD$C"

# Superset webserver config
SUPERSET_WEBSERVER_PORT = 8088

# Enable embedding in iframe
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['http://localhost:5000', 'http://127.0.0.1:5000']
}

# Allow embedding dashboards
PUBLIC_ROLE_LIKE = "Gamma"
TALISMAN_ENABLED = False
WTF_CSRF_ENABLED = False

# Feature flags
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "EMBEDDED_SUPERSET": True,
    "EMBEDDABLE_CHARTS": True,
    "DASHBOARD_RBAC": True,
}

# Guest token for embedding
GUEST_ROLE_NAME = "Public"
GUEST_TOKEN_JWT_SECRET = "Jx8kF2!9vQmP@eR7#WzYB4A6Hn0sD$C"
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"
GUEST_TOKEN_JWT_EXP_SECONDS = 300
