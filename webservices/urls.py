from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from webservices import views
from rest_framework.documentation import include_docs_urls

GET_SAMPLE_INGESTION = url(
    regex=r'^sample-ingestion/(?P<name_and_gene_collection>[A-za-z0-9\-_]+[^/])/*$',
    view=views.SampleIngestionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
    name='get-sample-ingestion'
)


LIST_CREATE_SAMPLE_INGESTION = url(
    regex=r'^sample-ingestion/$',
    view=views.SampleIngestionViewSet.as_view({'get': 'list', 'post': 'create'}),
    name='list-sample-ingestion'
)


GET_DELETE_PROPERTY_DEFINITION = url(
    regex=r'^property-definition/(?P<property_name>[A-za-z0-9\-_]+[^/])$',
    view=views.PropertyDefinitionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
    name='get-property-definition'
)


LIST_CREATE_PROPERTY_DEFINITION = url(
    regex=r'^property-definition/$',
    view=views.PropertyDefinitionViewSet.as_view({'get': 'list', 'post': 'create'}),
    name='list-property-definition'
)

GET_DELETE_GENE_COLLECTION = url(
    regex=r'^gene-collection/(?P<name>[A-za-z0-9\-_]+[^/])$',
    view=views.GeneCollectionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'}),
    name='get-gene-collection'
)


LIST_CREATE_GENE_COLLECTION = url(
    regex=r'^gene-collection/$',
    view=views.GeneCollectionViewSet.as_view({'get': 'list', 'post': 'create'}),
    name='list-gene-collection'
)

LIST_GENE_COVERAGE = url(
    regex=r'^gene-coverage/$',
    view=views.GeneCoverageView.as_view({'post': 'list'}),
    name='gene-coverage-list'
)

GET_GENE_COVERAGE = url(
    regex=r'^gene-coverage/(?P<sample_name>[A-za-z0-9\-_]+)/(?P<gene_collection>[A-za-z0-9\-_]+)/(?P<gene>[A-za-z0-9\-_]+[^/])$',
    view=views.GeneCoverageView.as_view({'get': 'retrieve'}),
    name='gene-coverage-detail'
)

LIST_SAMPLE_METRICS = url(
    regex=r'^sample-metrics/$',
    view=views.SampleMetricsView.as_view({'post': 'list'}),
    name='sample-metrics-list'
)

GET_SAMPLE_METRICS = url(
    regex=r'^sample-metrics/(?P<sample_name>[A-za-z0-9\-_]+)/(?P<gene_collection>[A-za-z0-9\-_]+[^/])$',
    view=views.SampleMetricsView.as_view({'get': 'retrieve'}),
    name='sample-metrics-detail'
)

TRANSCRIPT_AGGREGATION = url(
    regex=r'^aggregation/union-transcript$',
    view=views.AggregationView.as_view({'post': 'list'}),
    name='aggregation-union-transcript'
)

schema_view = get_schema_view(
   openapi.Info(
      title="Calypso",
      default_version='v1',
      description="Calypso is a service to store and analyse coverage metrics from whole genome sequences",
   ),
   public=True,
)

urls = [LIST_CREATE_SAMPLE_INGESTION,
        GET_SAMPLE_INGESTION,
        GET_GENE_COVERAGE,
        LIST_GENE_COVERAGE,
        GET_SAMPLE_METRICS,
        LIST_SAMPLE_METRICS,
        LIST_CREATE_GENE_COLLECTION,
        GET_DELETE_GENE_COLLECTION,
        LIST_CREATE_PROPERTY_DEFINITION,
        GET_DELETE_PROPERTY_DEFINITION,
        TRANSCRIPT_AGGREGATION,
        url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui')
        ]


urlpatterns = format_suffix_patterns(urls)
