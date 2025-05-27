import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "5000")
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Limit max workers to 4
worker_class = 'gthread'
threads = 4  # Increased threads per worker
worker_connections = 2000
timeout = 180  # Increased timeout
keepalive = 5  # Increased keepalive

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
max_requests = 500  # Reduced to recycle workers more frequently
max_requests_jitter = 50
worker_tmp_dir = '/tmp'

# Graceful timeout
graceful_timeout = 120

# Preload app
preload_app = True

# Worker recycling
max_worker_lifetime = 3600  # Restart workers after 1 hour
max_worker_lifetime_jitter = 60  # Add some randomness to worker lifetime

# Error handling
capture_output = True
enable_stdio_inheritance = True

# Worker class settings
worker_class = 'gthread'
threads = 4 
