from coveragedata.constants import VALUES
from coveragedata.coverage_manager import CoverageManager


class Stats(object):
    __slots__ = [
        'pct75', 'bases', 'med', 'gte30x', 'gte15x', 'pct25', 'avg', 'lt15x', 'gc', 'gte50x',
        'other_stats'
    ]

    def __init__(self, **kwargs):
        self.pct75 = kwargs.get('pct75', None)
        self.bases = kwargs.get('bases', None)
        self.med = kwargs.get('med', None)
        self.gte30x = kwargs.get('%>=30x', None)
        self.gte50x = kwargs.get('%>=50x', None)
        self.gte15x = kwargs.get('%>=15x', None)
        self.lt15x = kwargs.get('%<15x', None)
        self.pct25 = kwargs.get('pct25', None)
        self.avg = kwargs.get('avg', None)
        self.gc = kwargs.get('gc', None)
        self.other_stats = {k: v for k, v in kwargs.items() if k not in VALUES}

    @classmethod
    def from_array(cls, array):
        return cls(**{k: v for v, k in zip(array, VALUES)})

    def to_json_dict(self):
        return {k: self.__getattribute__(k) for k in self.__slots__}


class ExonCoverage(object):
    __slots__ = ['padded_s', 'padded_e', 'stats', 'gaps']

    def __init__(self, **kwargs):
        self.padded_s = kwargs.get('padded_s', None)
        self.padded_e = kwargs.get('padded_e', None)
        self.stats = Stats.from_array(kwargs.get('stats', None))
        self.gaps = kwargs.get('gaps', None)

    def to_json_dict(self):
        return {k: (self.__getattribute__(k) if k != 'stats' else self.__getattribute__(k).to_json_dict())
                for k in self.__slots__}


class TranscriptCoverage(object):
    __slots__ = ['name', 'exons', 'stats']

    def __init__(self, **kwargs):
        self.name = kwargs.get('id', None)
        self.exons = [ExonCoverage(**e) for e in kwargs.get('exons', None)]
        self.stats = Stats(**kwargs.get('stats', None))

    def to_json_dict(self):
        return {'exons': [e.to_json_dict() for e in self.exons],
                'name': self.name,
                'stats': self.stats.to_json_dict()
                }


class GeneCoverage(object):
    __slots__ = [
        'name', 'union_transcript', 'gen_collection', 'transcripts',
        'sample'
    ]

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.union_transcript = TranscriptCoverage(**kwargs.get('union_tr', None))
        self.gen_collection = kwargs.get('gcol', None)
        self.transcripts = [TranscriptCoverage(**t) for t in kwargs.get('trs', None)]
        self.sample = kwargs.get('sample', None)

    @classmethod
    def get(cls, gene_name, gene_collection, sample):
        """

        :type sample: str
        :type gene_name: str
        """

        cm = CoverageManager()
        result = cm.get_gene_info(sample, gene_collection, gene_name)
        return cls(**result.next())

    @classmethod
    def list(cls, sample, gene_list, gene_collection, last_gene=None, limit=None):
        cm = CoverageManager()
        results = cm.get_sample_info(sample, gene_collection, gene_list, last_gene, limit)
        for r in results:
            yield cls(**r)

    def to_json_dict(self):
        return {'name': self.name,
                'union_transcript': self.union_transcript.to_json_dict(),
                'gen_collection': self.gen_collection,
                'transcripts': [t.to_json_dict() for t in self.transcripts],
                'sample': self.sample
                }
