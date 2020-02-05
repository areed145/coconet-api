# web: hypercorn -b 0.0.0.0:${PORT} -w 4 -k uvloop app:app
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --timeout 20 --preload