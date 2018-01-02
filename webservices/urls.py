from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from webservices import views
from rest_framework.documentation import include_docs_urls

GET_SAMPLE_INGESTION = url(
    regex=r'^sample-ingestion/(?P<name_and_gene_collection>[A-za-z0-9\-_]+)/$',
    view=views.SampleIngestionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
    name='get-sample-ingestion'
)


LIST_CREATE_SAMPLE_INGESTION = url(
    regex=r'^sample-ingestion/$',
    view=views.SampleIngestionViewSet.as_view({'get': 'list', 'post': 'create'}),
    name='list-sample-ingestion'
)

LIST_GENE_COVERAGE = url(
    regex=r'^gene-coverage/(?P<sample_name>[A-za-z0-9\-_]+)/$',
    view=views.GeneCoverageView.as_view({'post': 'list'}),
    name='gene-coverage-list'
)

GET_GENE_COVERAGE = url(
    regex=r'^gene-coverage/(?P<sample_name>[A-za-z0-9\-_]+)/(?P<gene_collection>[A-za-z0-9\-_]+)/(?P<gene>[A-za-z0-9\-_]+)/$',
    view=views.GeneCoverageView.as_view({'get': 'retrieve'}),
    name='gene-coverage-detail'
)


DOCS = url(r'^docs/', include_docs_urls(title='Coverage DB API'))

urls = [LIST_CREATE_SAMPLE_INGESTION,
        GET_SAMPLE_INGESTION,
        GET_GENE_COVERAGE,
        LIST_GENE_COVERAGE,

        DOCS

        ]


urlpatterns = format_suffix_patterns(urls)
