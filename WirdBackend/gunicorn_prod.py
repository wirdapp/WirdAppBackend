import multiprocessing
import os

# Worker configuration
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True

# Process naming
proc_name = 'wird_backend'
pidfile = '/var/run/gunicorn/prod.pid'

# Binding
bind = '0.0.0.0:8000'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
