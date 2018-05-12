from pandas import DataFrame, np
from pandas.io.json import json_normalize

from coveragedata.coverage_manager import *


class UnionTranscriptsAggregation(object):
    raw_data = None
    df = None

    def __init__(self, samples=None, gene_list=None, experiment=None):
        self.experiment = experiment
        self.gene_list = gene_list
        self.samples = samples

    def _fetch_data(self):
        coverage_manager = CoverageManager()
        mongodb_cursor = coverage_manager.get_coverage_by_sample_and_genes(samples=self.samples,
                                                                           gene_list=self.gene_list,
                                                                           experiment=self.experiment
                                                                           )
        self.raw_data = [u for u in mongodb_cursor]

    def _load_data(self):
        if self.raw_data is None:
            self._fetch_data()
        self.df = DataFrame(json_normalize(self.raw_data))
        self.df = self.df.set_index(['name', 'sample'])

    def to_json_dict(self, mode: str = 'index') -> dict:
        """

        :param mode: `index`: Gene will be the key, `list`: column is the key, data is an array
        :return:
        """
        if self.df is None:
            self._load_data()
        return self.expand_dict(self.df.groupby('name').describe(include=[np.number], percentiles=[]).to_dict(mode))

    def expand_dict(self, result_dict, lstrip='union_tr.stats.'):
        new_dict = {}
        for key in result_dict:
            new_dict.setdefault(key, {})
            for comp_key in result_dict[key]:
                new_dict[key].setdefault(comp_key[0].replace(lstrip, ''), {})
                new_dict[key][comp_key[0].replace(lstrip, '')][comp_key[1]] = round(result_dict[key][comp_key], 3)
        return new_dict
