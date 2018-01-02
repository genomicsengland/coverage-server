from django.contrib import admin

from .models import SampleIngestion, GeneCollection


class SampleIngestionAdmin(admin.ModelAdmin):
    list_display = ['name', 'input_file', 'gene_collection', 'task']


class GeneCollectionAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(SampleIngestion, SampleIngestionAdmin)
admin.site.register(GeneCollection, GeneCollectionAdmin)
