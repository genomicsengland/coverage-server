from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from coveragedbingestion.models import SampleIngestion, PropertyDefinition, CollectionProperty, GeneCollection


class StringListField(serializers.ListField):
    child = serializers.CharField()


class GeneCoverageQuery(object):
    def __init__(self, gene_collection, gene_list, last_gene):
        self.last_gene = last_gene
        self.gene_collection = gene_collection
        self.gene_list = gene_list


class AggregationQuery(object):
    def __init__(self, gene_list):
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


class AggregationsSerializer(serializers.Serializer):
    gene_list = StringListField(help_text='List of genes names, i.e TP53')

    def to_representation(self, instance):
        return instance.to_json_dict()

    def to_internal_value(self, data):
        return AggregationQuery(gene_list=data.get('gene_list'))


class PropertyDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDefinition
        fields = ('property_name', 'property_type')

    def create(self, validated_data):
        return PropertyDefinition.objects.create(**validated_data)


class CollectionPropertySerializer(serializers.ModelSerializer):
    property_type = PrimaryKeyRelatedField(many=False, queryset=PropertyDefinition.objects.all())

    class Meta:
        model = CollectionProperty
        fields = ('property_type', 'value')

    def validate(self, data):
        if data.get('property_type').property_type == 'float':
            try:
                float(data.get('value'))
            except ValueError:
                raise serializers.ValidationError('Please provide a valid float value')

        elif data.get('property_type').property_type == 'integer':
            try:
                int(data.get('value'))
            except ValueError:
                raise serializers.ValidationError('Please provide a valid integer value')
        return data


class GeneCollectionSerializer(serializers.ModelSerializer):
    properties = CollectionPropertySerializer(many=True)

    class Meta:
        model = GeneCollection
        fields = ('name', 'properties')

    def create(self, validated_data):
        properties = validated_data.pop('properties')
        gene_collection = GeneCollection.objects.create(**validated_data)
        for p in properties:
            property_type = p['property_type']
            CollectionProperty.objects.create(value=p['value'],
                                              property_type=property_type,
                                              collection=gene_collection)
        return gene_collection

    def update(self, instance, validated_data):
        properties = validated_data.pop('properties')
        instance.name = validated_data.get('name', instance.name)
        for p in properties:
            property_type = p['property_type']
            CollectionProperty.objects.update_or_create(property_type=property_type,
                                                        collection=instance,
                                                        defaults={'value': p['value']})
        instance.save()
        return instance





