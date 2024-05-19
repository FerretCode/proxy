FROM python:alpine-3.11.9 AS builder

ENV PORT=3000
EXPOSE 3000

ENTRYPOINT [ "python", "proxy.py" ]