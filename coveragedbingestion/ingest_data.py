import json

from coveragedata.constants import STATS_ORDERED_KEYS, EXON_EXCLUDED_KEYS
from coveragedata.coverage_manager import CoverageManager
from coveragedata.sample_manager import SampleManager


def build_coverage_document(sample, genes, gene_collection):
    for gene in genes:
        yield {**{'sample': sample, 'gcol': gene_collection}, **gene}


def convert_gaps(gaps):
    return list(map(lambda p: (p['s'], p['e']), list(filter(lambda x: x['e'] - x['s'] > 5, gaps))))


def clean_exon(exon, excluded_keys=EXON_EXCLUDED_KEYS, stats_ordered_keys=STATS_ORDERED_KEYS):
    exon['gaps'] = convert_gaps(gaps=exon.get('gaps', []))
    exon['stats'] = [exon['stats'][key] for key in stats_ordered_keys]
    list(map(lambda k: exon.pop(k), excluded_keys))


def minimize_exons(gene_data):
    list(map(lambda exon: clean_exon(exon), gene_data['exons']))


def minimize_gene(gene):
    minimize_exons(gene['union_tr'])
    list(map(lambda gene_data: minimize_exons(gene_data), gene['trs']))


def transform_data(data):
    list(map(lambda gene: minimize_gene(gene), data))
    return data


def ingest_data(input_file, sample, gene_collection_id):
    with open(input_file) as fd:
        j = json.load(fd)

    parameters = j['parameters']
    coding_region = j.get('results', {}).get('coding_region', {})
    genes = transform_data(j.get('results', {}).get('genes', []))
    nog = len(genes)
    whole_genome = j.get('results', {}).get('whole_genome', {})
    cm = CoverageManager()
    sm = SampleManager()

    sm.add_sample(sample_name=sample, number_of_genes=nog, parameters=parameters, coding_region=coding_region,
                  whole_genome=whole_genome, gene_collection=gene_collection_id
                  )
    cm.add_coverage_data(build_coverage_document(sample, genes, gene_collection_id))



