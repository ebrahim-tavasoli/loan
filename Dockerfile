FROM python:3.13-slim

ARG PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y curl weasyprint && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install uv
RUN apt-get update && apt-get install -y locales git
RUN sed -i '/fa_IR.UTF-8/s/^# //' /etc/locale.gen && \
    locale-gen
ENV LANG fa_IR.UTF-8
ENV LC_ALL fa_IR.UTF-8

COPY pyproject.toml .
COPY uv.lock .
COPY .python-version .
RUN uv sync --no-dev --locked

COPY . .

RUN chmod +x manage.py

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "loan.wsgi:application", "--bind", "0.0.0.0:8000"]