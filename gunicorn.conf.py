import multiprocessing
import os
import sys

# Server socket
bind = "0.0.0.0:" + os.getenv("PORT", "5000")
backlog = 2048

# Worker processes
workers = 2  # Reduced number of workers
worker_class = 'sync'  # Changed to sync for lower memory usage
worker_connections = 1000
timeout = 180
keepalive = 5

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
    worker.alive = False

def worker_abort(worker):
    """Log when worker receives SIGABRT"""
    worker.log.info("Worker received SIGABRT")
    worker.alive = False

def worker_exit(server, worker):
    """Log worker exit"""
    try:
        # Get exit code safely for both process and thread workers
        exit_code = getattr(worker, 'exit_code', None)
        if exit_code is None:
            # For thread workers, try to get exit code from process
            exit_code = getattr(worker, 'process', None)
            if exit_code is not None:
                exit_code = getattr(exit_code, 'exitcode', None)
        
        # Log the exit with available information
        if exit_code is not None:
            server.log.info(f"Worker {worker.pid} exited with code {exit_code}")
        else:
            server.log.info(f"Worker {worker.pid} exited")
    except Exception as e:
        server.log.error(f"Error in worker exit handler: {str(e)}")

# Memory management
max_requests = 100  # Reduced to recycle workers more frequently
max_requests_jitter = 10
worker_tmp_dir = '/tmp'

# Graceful timeout
graceful_timeout = 120

# Preload app
preload_app = True

# Worker recycling
max_worker_lifetime = 1800  # Restart workers after 30 minutes
max_worker_lifetime_jitter = 30

# Error handling
capture_output = True
enable_stdio_inheritance = True

# Memory limits
worker_memory_limit = 256 * 1024 * 1024  # 256MB per worker

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
