import logging

import pymongo
from pymongo import MongoClient

from coveragedb.settings import COVERAGE_DB, COVERAGE_DB_HOST

COLLECTIONS = (
    'genes',
    'samples',
    'coverage'
)

INDEXES = {
    'samples': [('name', {'unique': True})],
    'coverage': [
        ([('_id', pymongo.ASCENDING)], {}),
        ([('sample', pymongo.ASCENDING), ('name', pymongo.ASCENDING)], {'unique': True}),
        ([
             ('name', pymongo.ASCENDING),
             ('union_tr.stats.med', pymongo.ASCENDING),
             ('union_tr.stats.gte15x', pymongo.ASCENDING),
             ('union_tr.stats.gte50x', pymongo.ASCENDING),
             ('union_tr.stats.avg', pymongo.ASCENDING),
             ('union_tr.stats.pct75', pymongo.ASCENDING),
             ('union_tr.stats.gte30x', pymongo.ASCENDING),
             ('union_tr.stats.pct25', pymongo.ASCENDING),
             ('union_tr.stats.bases', pymongo.ASCENDING),
             ('union_tr.stats.sd', pymongo.ASCENDING),
             ('union_tr.stats.lt15x', pymongo.ASCENDING),
         ],
         {'name': 'stats'}
        )
    ]
}


def check_db():
    logging.info('Connecting to {}'.format(COVERAGE_DB_HOST))
    c = MongoClient(host=COVERAGE_DB_HOST)
    logging.info('Selecting DB {}'.format(COVERAGE_DB))
    coverage_db = c[COVERAGE_DB]
    av_collections = coverage_db.collection_names(include_system_collections=False)
    logging.debug('{} collections has been found'.format(', '.join(av_collections)))
    for col in COLLECTIONS:
        if col not in av_collections:
            logging.info('Creating {} collection'.format(col))
            coverage_db.create_collection(name=col)
    logging.info('All done.')


def check_indexes():
    logging.info('Connecting to {}'.format(COVERAGE_DB_HOST))
    c = MongoClient(host=COVERAGE_DB_HOST)
    logging.info('Selecting DB {}'.format(COVERAGE_DB))
    coverage_db = c[COVERAGE_DB]

    for col in COLLECTIONS:
        for index in INDEXES.get(col, []):
            coverage_db[col].create_index(index[0], **index[1])
            logging.info('Creating index "{}" with parameters "{}"'.format(str(index[0]), str(index[1])))
    logging.info('All done.')


logging.basicConfig(level=logging.DEBUG)
check_db()
check_indexes()
