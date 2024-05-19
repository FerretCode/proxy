FROM python:3.11.9-alpine

WORKDIR /app

COPY . .

EXPOSE 3000

ENTRYPOINT [ "python", "proxy.py" ]