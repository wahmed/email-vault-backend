FROM python:3.10-slim
WORKDIR /app
COPY .env .env_secrets /app/

COPY my_flask/requirements.txt ./my_flask/

RUN pip install --no-cache-dir -r my_flask/requirements.txt

COPY . .

ENV FLASK_APP=my_flask.app
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run"]
