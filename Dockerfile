FROM python:2.7

ADD . /Athena-Exporter
RUN pip install -r /Athena-Exporter/pip-requirements.txt

WORKDIR /Athena-Exporter
ENV PYTHONPATH '/Athena-Exporter/'

CMD ["python" , "/Athena-Exporter/AthenaExporter.py"]

MAINTAINER Pedro Reichmann