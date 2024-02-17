import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
# Write access and error info to /var/log
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = "/var/run/gunicorn/prod.pid"
bind = "0.0.0.0:8000"
daemon = True