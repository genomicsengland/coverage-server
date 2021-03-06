from django.db import models
from django.utils.text import slugify
from django_celery_results.models import TaskResult

from coveragedata.coverage_manager import CoverageManager
from coveragedata.sample_manager import SampleManager
from coveragedbingestion.tasks import ingest


class GeneCollection(models.Model):
    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name


class SampleIngestion(models.Model):
    name = models.CharField(max_length=50)
    input_file = models.CharField(max_length=1000)
    gene_collection = models.ForeignKey(GeneCollection, on_delete=models.CASCADE)
    task = models.ForeignKey(TaskResult, on_delete=models.CASCADE, default=None, null=True)
    name_slug = models.SlugField(max_length=200, unique=True, editable=False, null=True)
    seconds = models.IntegerField(default=None, null=True)

    class Meta:
        unique_together = ('name', 'gene_collection',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name_slug = '-'.join((slugify(self.name), slugify(self.gene_collection.name)))
        if self.pk is None:
            super(SampleIngestion, self).save(force_insert, force_update, using, update_fields)
            ingest.delay(self.pk)
        else:
            super(SampleIngestion, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        cm = CoverageManager()
        sm = SampleManager()
        cm.remove_coverage_data(self.name, self.gene_collection.name)
        sm.remove_sample(self.name, self.gene_collection.name)
        delete_stats = super(SampleIngestion, self).delete(using=None, keep_parents=False)
        return delete_stats
