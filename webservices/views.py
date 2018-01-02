from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework import viewsets, mixins, pagination
from rest_framework.decorators import list_route, detail_route

from coveragedata.models import GeneCoverage
from coveragedata.sample_manager import SampleManager
from coveragedbingestion.models import SampleIngestion
from webservices.serializers import SampleIngestionSerializer, CoverageSerializer, SampleCoverageSerializer


class SampleIngestionViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             viewsets.GenericViewSet):
    """
    A simple ViewSet for viewing SampleIngestion.

    retrieve:
    Return SampleIngestion.

    """
    queryset = SampleIngestion.objects.all()
    serializer_class = SampleIngestionSerializer
    lookup_field = 'name_slug'
    lookup_url_kwarg = 'name_and_gene_collection'


class GeneCoveragePagination(pagination.BasePagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(data),
            'results': data[0]
        })

    def get_next_link(self, data):
        if data[0] and len(data[0]) <= data[1]:
            return reverse_lazy('gene-coverage-list') + '?page={}'.format(data[0][-1]['name'])
        return None


class SampleMetricsPagination(pagination.BasePagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(data),
            'results': data[0]
        })

    def get_next_link(self, data):
        if data[0] and len(data[0]) <= data[1]:
            return reverse_lazy('sample-metrics-list') + '?page={}'.format(data[0][-1]['name'])
        return None


class GeneCoverageView(viewsets.ViewSet):
    """

    list:
    List of Coverage data
        sample_name: Name of the requested sample
    """
    model = GeneCoverage
    serializer = CoverageSerializer
    page_size = 100
    pagination = GeneCoveragePagination()

    def get_sample_page(self, sample_name, gene_collection, gene_list, last_gene):
        return self.model.list(sample_name, gene_list, gene_collection, last_gene, limit=self.page_size)

    def get_sample_gene_info(self, sample, gene_collection, gene):
        return self.model.get(sample=sample, gene_collection=gene_collection, gene_name=gene)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.serializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    @list_route(methods=['post'])
    def list(self, request):

        r = self.get_sample_page(request.data.get('sample_name', ''), request.data.get('gene_collection', ''),
                                 request.data.get('gene_list', []), request.query_params.get('page')
                                 )
        s = self.serializer(instance=r, many=True)
        paginated_response = self.pagination.get_paginated_response([s.data, self.page_size])
        return paginated_response

    def retrieve(self, request, sample_name, gene_collection, gene):
        r = self.get_sample_gene_info([sample_name], gene_collection, gene)
        s = self.serializer(instance=r, many=False)
        return Response(s.data)


class SampleMetricsView(viewsets.ViewSet):
    """

    list:
    List of Coverage data
        sample_name: Name of the requested sample
    """
    sample_manager = SampleManager()
    serializer = SampleCoverageSerializer
    page_size = 100
    pagination = SampleMetricsPagination()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.serializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_sample_page(self, sample_list, gene_collection, last_sample=None):
        return self.sample_manager.get_sample_info(sample_list=sample_list, gene_collection=gene_collection,
                                                   last_sample=last_sample, limit=self.page_size
                                                   )

    @list_route(methods=['post'])
    def list(self, request):

        r = self.get_sample_page(gene_collection=request.data.get('gene_collection', ''),
                                 sample_list=request.data.get('sample_list', []),
                                 last_sample=request.query_params.get('page')
                                 )
        s = self.serializer(instance=r, many=True)
        paginated_response = self.pagination.get_paginated_response([s.data, self.page_size])
        return paginated_response

    def retrieve(self, request, sample_name, gene_collection):
        r = self.get_sample_page([sample_name], gene_collection)
        s = self.serializer(instance=r.next(), many=False)
        return Response(s.data)


