
import os
import multiprocessing

PORT = os.environ['PORT']
DEBUG_MODE = os.environ['DEBUG_MODE']

# Gunicorn config
bind = ":" + str(PORT)
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()