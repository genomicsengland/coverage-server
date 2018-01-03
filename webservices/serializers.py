from rest_framework import serializers

from coveragedata.models import GeneCoverage
from coveragedbingestion.models import SampleIngestion


class StringListField(serializers.ListField):
    child = serializers.CharField()


class GeneCoverageQuery(object):
    def __init__(self, gene_collection, gene_list, last_gene):
        self.last_gene = last_gene
        self.gene_collection = gene_collection
        self.gene_list = gene_list



class SampleIngestionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = SampleIngestion
        fields = ['name', 'input_file', 'gene_collection', 'task', 'status']

    def get_status(self, obj):
        try:
            return obj.task.status
        except:
            return 'NOT STARTED'


class CoverageSerializer(serializers.Serializer):
    gene_collection = serializers.CharField(help_text='Name of the Gene Collection, '
                                                      'you can check the available gene collection in'
                                                      '/api/gene-collection/')
    gene_list = StringListField(help_text='List of genes names, i.e TP53')
    sample_name = serializers.CharField(help_text='Sample name')

    def to_representation(self, instance):
        return instance.to_json_dict()

    def to_internal_value(self, data):
        return GeneCoverageQuery(gene_list=data.get('gene_list'), gene_collection=data.get('gene_collection', []),
                                 last_gene=data.get('last_gene')
                                 )


class SampleCoverageSerializer(serializers.Serializer):
    gene_collection = serializers.CharField()
    sample_list = StringListField()

    def to_representation(self, instance):
        instance.pop('_id')
        return instance




