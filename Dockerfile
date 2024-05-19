FROM python:3.11.9-alpine

WORKDIR /app

COPY . .

ENV PORT=3000
EXPOSE 3000

ENTRYPOINT [ "python", "proxy.py" ]