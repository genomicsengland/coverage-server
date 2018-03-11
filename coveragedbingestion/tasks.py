# Create your tasks here
import logging
import time

from celery import shared_task, states
from django.apps import apps
from django_celery_results.models import TaskResult
from coveragedbingestion.ingest_data import ingest_data


@shared_task
def ingest(sample_ingest_id):
    sample_ingestion_model = apps.get_model('coveragedbingestion', 'SampleIngestion')
    logging.info(sample_ingestion_model)
    sample_ingest = sample_ingestion_model.objects.get(id=sample_ingest_id)
    task_id = ingest.request.id
    logging.info("Starting task with id '{}'".format(task_id))
    # saves the task in pending status
    task_result = TaskResult(task_id=task_id)
    task_result.save()
    # associates the task to the sample ingestion entity
    sample_ingest.task = task_result
    sample_ingest.save()
    start_time = time.time()
    try:
        ingest_data(input_file=sample_ingest.input_file, sample=sample_ingest.name,
                    gene_collection_id=sample_ingest.gene_collection.name)
        seconds = time.time() - start_time
        logging.info("Task succeeded in {} seconds!".format(seconds))
        sample_ingest.seconds = int(seconds)
        sample_ingest.save(update_fields=["seconds"])
        # TODO: do we need this?
        task_result.status = states.SUCCESS
        task_result.save(update_fields=["status"])
    except Exception as ex:
        seconds = time.time() - start_time
        sample_ingest.seconds = int(seconds)
        sample_ingest.save(update_fields=["seconds"])
        logging.error("Task failed: {}".format(str(ex)))
        # TODO: do we need this?
        task_result.status = states.FAILURE
        task_result.save(update_fields=["status"])
