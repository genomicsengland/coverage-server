import json

from coveragedata.constants import VALUES
from coveragedata.coverage_manager import CoverageManager
from coveragedata.sample_manager import SampleManager


def add_sample(sample, genes, gene_collection):
    for gene in genes:
        yield {**{'sample': sample, 'gcol': gene_collection}, **gene}


def convert_gaps(gaps):
    return list(map(lambda p: (p['s'], p['e']), list(filter(lambda x: x['e'] - x['s'] > 5, gaps))))


def clean_exon(exon, keys=('exon', 's', 'l', 'e'), ordered_values=VALUES):
    exon['gaps'] = convert_gaps(gaps=exon['gaps'])
    exon['stats'] = [exon['stats'][o] for o in ordered_values]
    list(map(lambda k: exon.pop(k), keys))


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
    coding_region = j['results']['coding_region']
    genes = transform_data(j['results']['genes'])
    nog = len(genes)
    whole_genome = j['results'].get('whole_genome')
    cm = CoverageManager()
    sm = SampleManager()

    sm.add_sample(sample_name=sample, number_of_genes=nog, parameters=parameters, coding_region=coding_region,
                  whole_genome=whole_genome, gene_collection=gene_collection_id
                  )
    cm.add_coverage_data(add_sample(sample, genes, gene_collection_id))



