FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin jaevis
COPY --chown=jaevis:jaevis app.py .
USER jaevis

EXPOSE 8080
CMD ["python", "app.py"]
