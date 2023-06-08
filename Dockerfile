FROM python:3.10

COPY . /api
WORKDIR /api

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

CMD ["python", "main.py"]