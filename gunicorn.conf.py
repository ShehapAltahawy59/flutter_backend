import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "5000")
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'fitness_api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Server hooks
def on_starting(server):
    """Log when server starts"""
    server.log.info("Starting fitness API server")

def on_exit(server):
    """Log when server exits"""
    server.log.info("Stopping fitness API server")

# Worker hooks
def worker_int(worker):
    """Log when worker receives SIGINT"""
    worker.log.info("Worker received SIGINT")

def worker_abort(worker):
    """Log when worker receives SIGABRT"""
    worker.log.info("Worker received SIGABRT")

# Memory management
max_requests = 1000
max_requests_jitter = 50
worker_tmp_dir = '/tmp'
worker_class = 'gthread'
threads = 2 
