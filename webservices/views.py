from django.urls import reverse_lazy
from rest_framework.response import Response
from rest_framework import viewsets, mixins, pagination
from rest_framework.decorators import list_route, detail_route

from coveragedata.models import GeneCoverage
from coveragedbingestion.models import SampleIngestion
from webservices.serializers import SampleIngestionSerializer, CoverageSerializer


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


class Pagination(pagination.BasePagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(data),
            'results': data[0]
        })

    def get_next_link(self, data):
        if data[0] and len(data[0]) <= data[1]:
            return reverse_lazy('gene-coverage-list', kwargs={
                "sample_name": data[0][-1]['sample']}
                                ) + '?page={}'.format(data[0][-1]['name'])
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
    pagination = Pagination()

    def get_sample_page(self, sample_name, gene_collection, gene_list, last_gene):
        return self.model.list(sample_name, gene_list, gene_collection, last_gene, limit=self.page_size)

    def get_sample_gene_info(self, sample, gene_collection, gene):
        return self.model.get(sample=sample, gene_collection=gene_collection, gene_name=gene)

    @list_route(methods=['post'])
    def list(self, request, sample_name):

        r = self.get_sample_page(sample_name, request.data.get('gene_collection', ''),
                                 request.data.get('gene_list', []), request.query_params.get('page')
                                 )
        s = self.serializer(instance=r, many=True)
        paginated_response = self.pagination.get_paginated_response([s.data, self.page_size])
        return paginated_response

    def retrieve(self, request, sample_name, gene_collection, gene):
        r = self.get_sample_gene_info([sample_name], gene_collection, gene)
        s = self.serializer(instance=r, many=False)
        return Response(s.data)



class SampleCoverageView(viewsets.ViewSet):
    """

    list:
    List of Coverage data
        sample_name: Name of the requested sample
    """
    model = GeneCoverage
    serializer = CoverageSerializer
    page_size = 100
    pagination = Pagination()

    # def get_sample_page(self, sample_name, gene_collection):
    #     return self.model.list(sample_name, gene_list, gene_collection, last_gene, limit=self.page_size)

    # @list_route(methods=['post'])
    # def list(self, request):
    #
    #     r = self.get_sample_page(sample_name, request.data.get('gene_collection', ''),
    #                              request.data.get('gene_list', []), request.query_params.get('page')
    #                              )
    #     s = self.serializer(instance=r, many=True)
    #     paginated_response = self.pagination.get_paginated_response([s.data, self.page_size])
    #     return paginated_response

