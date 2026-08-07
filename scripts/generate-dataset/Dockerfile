FROM python:3.8

ENV LOG_LEVEL="info"

RUN mkdir /templates
COPY minister-new-dcat-dataset.ttl /templates
RUN pip install rdflib==7.0.0 pytz==2024.1
