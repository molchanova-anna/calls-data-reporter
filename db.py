'''
Connection to mongo
Aggregation data query
'''
from pymongo import MongoClient
from config import config


class DBConnector:
    client = None
    db = None
    collection = None

    def __enter__(self):
        client = MongoClient(config.mongodb_url)
        self.client = client
        self.db = client.get_database(name=config.MONGODB_DB_NAME)
        self.collection = self.db.calls
        return self

    def __exit__(self, *args):
        pass


def get_stat_for_calls_list(ids: list):
    with DBConnector() as conn:
        pipe_filter_by_id = {'$match': {'phone': {'$in': [i for i in ids]}}}

        expr_duration = {'$divide': [{'$sum': ["$end_date", {'$multiply': ['$start_date', -1]}]}, 3600]}
        pipe_field_set = {'$project' :
                              {'phone': 1,
                               'duration': expr_duration,
                               'price': {'$multiply': [expr_duration, 10]}}
                          }

        pipe_group = {'$group': {'_id':'$phone',
                                'cnt_all_attempts':{'$sum':1},
                                'cnt_att_dur_10_sec': {
                                    '$sum': {'$cond': [{'$lt': ["$duration", 10]}, 1, 0]}},
                                'cnt_att_dur_10_30_sec': {
                                    '$sum': {'$cond': [{'$and': [{'$gte': ['$duration', 10]}, {'$lte': ['$duration', 30]}]}, 1, 0]}},
                                'cnt_att_dur_30_sec': {
                                    '$sum': {'$cond': [{'$gt': ["$duration", 30]}, 1, 0]}},
                                'min_price_att': {
                                    '$min': '$price'},
                                'max_price_att': {
                                    '$max': '$price'},
                                'avg_dur_att': {
                                    '$avg': '$duration'},
                                'sum_price_att_over_15': {
                                    '$sum': {'$cond': [{'$gt': ['$duration', 15]}, '$price', 0]},
                                }
                                }}
        pipe_include_fields = {'$addFields': {'cnt_att_dur': {'10_sec': '$cnt_att_dur_10_sec',
                                                              '10_30_sec': '$cnt_att_dur_10_30_sec',
                                                              '30_sec': '$cnt_att_dur_30_sec'}}}

        pipe_exclude_fields = {'$project': {'_id': 0,
                                            'cnt_att_dur_10_sec': 0,
                                            'cnt_att_dur_10_30_sec': 0,
                                            'cnt_att_dur_30_sec': 0}}

        cur = conn.collection.aggregate([pipe_filter_by_id,
                                         pipe_field_set,
                                         pipe_group,
                                         pipe_include_fields,
                                         pipe_exclude_fields])
        res = [doc for doc in cur]
        return res
