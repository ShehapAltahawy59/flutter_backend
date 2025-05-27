import multiprocessing
import os
import sys
from startup import on_starting

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
def on_exit(server):
    """Log when server exits"""
    server.log.info("Stopping fitness API server")

# Worker hooks
def worker_int(worker):
    """Log when worker receives SIGINT"""
    worker.log.info("Worker received SIGINT")
    worker.alive = False

def worker_abort(worker):
    """Log when worker receives SIGABRT"""
    worker.log.info("Worker received SIGABRT")
    worker.alive = False

def worker_exit(server, worker):
    """Log when worker exits"""
    server.log.info(f"Worker {worker.pid} exited with code {worker.exit_code}")

def post_fork(server, worker):
    """Initialize worker after fork"""
    server.log.info(f"Worker {worker.pid} started")

def pre_fork(server, worker):
    """Initialize worker before fork"""
    pass

def pre_exec(server):
    """Initialize server before exec"""
    server.log.info("Forked child, re-executing.")

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

# Restart settings
reload = True
reload_extra_files = []
reload_engine = 'auto'

# Error recovery
max_worker_restarts = 10
worker_restart_delay = 5

# Memory limits
worker_memory_limit = 512 * 1024 * 1024  # 512MB per worker

def worker_restart(worker):
    """Handle worker restart"""
    worker.log.info(f"Worker {worker.pid} restarting...")
    return True

def worker_error(worker):
    """Handle worker error"""
    worker.log.error(f"Worker {worker.pid} encountered an error")
    return True

# Worker class settings
worker_class = 'gthread'
threads = 4 
