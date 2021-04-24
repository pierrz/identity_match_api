FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./data /data
COPY ./app /app
RUN pip install --upgrade pip
RUN pip install -r requirements/default.txt
RUN pip install -e .
