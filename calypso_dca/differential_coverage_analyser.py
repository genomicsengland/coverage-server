from coveragedata.coverage_manager import CoverageManager
import numpy
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri as numpy2ri
import rpy2.robjects.pandas2ri as pandas2ri
from pandas import DataFrame
import os


class DifferentialCoverageAnalyser(object):

    def __init__(self, groups):
        """
        PRE: the list of groups has exactly two groups
        :param groups: the list of groups to compare
        """
        numpy2ri.activate()  # this is required to transform numpy arrays into R data frames
        pandas2ri.activate()  # this is required to transform R data frames into pandas
        if groups is None or len(groups) != 2:
            raise ValueError("Only pairwise comparisons are supported!")
        self.groups = groups
        self.coverage_manager = CoverageManager()
        self.coverages, self.experimental_design, self.totals, self.genes, self.samples = self._load_data()
        self.dca_results = None

    def run(self):
        """
        Runs the differential coverage analysis
        :return:
        """
        self.dca_results = self._run_edger(self.coverages, self.experimental_design, self.totals)
        return self.dca_results

    def save_raw_data(self, folder):
        """
        Converts all data into Pandas data frames and saves to disk, including results if analysis ran
        :param folder:
        :return:
        """
        self.coverages.to_csv(os.path.join(folder, "coverages.csv"), sep='\t', encoding='utf-8')
        totals_df = DataFrame(self.totals, index=self.samples)
        totals_df.to_csv(os.path.join(folder, "totals.csv"), sep='\t', encoding='utf-8')
        experimental_design_df = DataFrame(self.experimental_design, index=self.samples)
        experimental_design_df.to_csv(os.path.join(folder, "experimental_design.csv"), sep='\t', encoding='utf-8')
        if self.dca_results is not None:
            self.dca_results.to_csv(os.path.join(folder, "dca_results.csv"), sep='\t', encoding='utf-8')

    def pprint_results(self, n=None):
        """
        Pretty print results
        :param n: show top N genes
        :return:
        """
        if self.dca_results is not None:
            print(self.dca_results[0:n])
        else:
            print("Run the analysis to see any results!")

    def _load_data(self):
        """
        Fetches all necessary data from the database and stores in memory
        :return:
        """
        samples = self.coverage_manager.get_samples_by_groups(self.groups)
        genes = self.coverage_manager.get_genes_by_groups(self.groups)
        coverages, totals = self._read_coverages(samples, genes)
        experimental_design = self._read_groups_by_samples(samples)
        return coverages, experimental_design, totals, genes, samples

    def _run_edger(self, coverages, experimental_design, totals):
        """
        Runs the Fisher's exact test to calculate differential coverage using edgeR.
        :param coverages: a pandas data frame data frame with coverage data (rows genes, columns samples)
        :param experimental_design: a unidimensional numpy array indicating the group of each sample
        :param totals: a unidimensional numpy array with the total coverage for each sample
        :return: a pandas data frame with one row per gene having fold change, p-value and adjusted p-value
        """
        robjects.r('''
            library(edgeR)
        ''')
        average_totals = numpy.mean(totals)
        # creates a constant array for library sizes, to avoid normalisation by depth of coverage
        sizes = [average_totals] * len(coverages.columns)
        params = {'group': numpy.transpose(experimental_design), 'lib.size': sizes}
        # loads data
        dgelist = robjects.r.DGEList(coverages, **params)
        # normalise by RNA composition, so highly expressed genes do not shadow others
        dgelist = robjects.r.calcNormFactors(dgelist)
        # estimate dispersions to calculate pseudo counts after adjusting by library size
        dgelist = robjects.r.estimateCommonDisp(dgelist)
        # performs Fisher exact test
        de = robjects.r.exactTest(dgelist)
        # adjusts for multiple testing and orders output by significance
        params = {"adjust.method": "fdr", "sort.by": "PValue"}
        tags = robjects.r.topTags(de, **params)
        # transforms to a pandas data frame
        results_table = pandas2ri.ri2py(tags[0])
        results_table["gene"] = tags[0].rownames  # stores the genes in the row names as a proper column in the data frame
        return results_table

    def _read_coverages_for_sample(self, sample, genes_with_indexes):
        """
        Returns a unidimensional arrays with the coverage for each gene. If there is no data for given gene a zero
        is returned in its place but the order of genes is maintained and the size of the array is independent of
        empty values.
        :param sample: the sample for which we want to read coverage data
        :param genes_with_indexes: a map with genes and their index in the output array
        :return: unidimensional numpy array with the list of coverages
        """
        cursor = self.coverage_manager.get_coverage_by_sample_and_genes(sample, list(genes_with_indexes.keys()))
        sample_coverages = numpy.zeros(shape=(len(genes_with_indexes)), dtype=int)
        for result in cursor:
            gene = result['name']
            # NOTE: we round to the nearest integer to use digital DGE methods
            coverage = int(round(result['union_tr']['stats']['avg']))
            sample_coverages[genes_with_indexes[gene]] = coverage
        return sample_coverages

    def _read_coverages(self, samples, genes):
        """

        :param samples: the list of samples for which we want to read coverage data
        :param genes: the ordered list of genes for which we want coverage data
        :return: pandas data frame with coverage data where rows correspond to genes and columns to samples,
        unidimensional array with total coverage for each sample
        """
        coverages = numpy.zeros(shape=(len(samples), len(genes)), dtype=int)
        totals = numpy.zeros(shape=(len(samples)), dtype=int)
        # computes the index of each gene only once
        genes_with_indexes = {gene: genes.index(gene) for gene in genes}
        sample_idx = 0
        for sample in samples:
            sample_coverages = self._read_coverages_for_sample(sample, genes_with_indexes)
            coverages[sample_idx] = sample_coverages
            totals[sample_idx] = numpy.sum(sample_coverages)
            sample_idx += 1
        coverages_df = DataFrame(data=numpy.transpose(coverages), index=genes, columns=samples)
        return coverages_df, totals

    def _read_groups_by_samples(self, samples):
        """
        PRE: all samples exist in the database
        :param samples: the list of samples of interest
        :return: a unidimensional numpy array with the groups (ie: gcol) in the same order as samples
        """
        results = self.coverage_manager.get_groups_by_samples(samples)
        groups = numpy.empty(shape=(len(samples)), dtype=object)
        for result in results:
            sample = result["_id"]
            group = result["group"]
            groups[samples.index(sample)] = group
        return groups
