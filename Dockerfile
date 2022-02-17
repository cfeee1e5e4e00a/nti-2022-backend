FROM python:latest

RUN pip install poetry

WORKDIR /app

ADD pyproject.toml poetry.lock ./

RUN poetry install

ADD src .env ./

CMD python src/main.py