FROM python:3.8

RUN pip install pipenv

WORKDIR /calls_data_reporter
ENV PYTHONPATH=./

COPY Pipfile Pipfile.lock ./
RUN PIPENV_VENV_IN_PROJECT=1
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install  --system --deploy

COPY . .

CMD ["python", "consumer.py"]