FROM python:3.10

WORKDIR /api
COPY . /api

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

CMD ["python", "main.py"]