# Create your tasks here
import logging

from celery import shared_task
from django.apps import apps
from django_celery_results.models import TaskResult
from coveragedbingestion.ingest_data import ingest_data



@shared_task
def ingest(sample_ingest_id):
    SampleIngestion = apps.get_model('coveragedbingestion', 'SampleIngestion')
    logging.info(SampleIngestion)
    sample_ingest = SampleIngestion.objects.get(id=sample_ingest_id)
    task_id = ingest.request.id
    logging.info(task_id)
    ingest_data(input_file=sample_ingest.input_file, sample=sample_ingest.name,
                gene_collection_id=sample_ingest.gene_collection.name)
    tr = TaskResult(task_id=task_id)
    tr.save()
    sample_ingest.task = tr
    logging.info(sample_ingest.task)
    sample_ingest.save()
