from datetime import datetime, timedelta

from config import ES_HOST, ES_PORT, INDEX_NAME
from dash.util import query
from typing import List, Any

from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])


def get_available_index():
    indices = es.indices.get(INDEX_NAME + '*')
    return [index for index in indices]


def get_uniq_item(elastic_field='kubernetes.labels.app.keyword'):
    query_service = {
        "sort": {
            "@timestamp": "desc"
        },
        "size": 0,
        "aggs": {
            "uniq_app": {"terms": {"field": elastic_field}}
        }
    }
    service_key = []
    start_time = datetime.utcnow() - timedelta(hours=1)
    end_time = datetime.utcnow()

    indices = query.get_queryable_indices(start_time=start_time, end_time=end_time)
    for index in indices:
        res = es.search(index=index, body=query_service)
        for item in res['aggregations']['uniq_app']['buckets']:
            service_key.append(item)
    return service_key


def get_data(keyword=None, start_time=None, end_time=None, service=None):
    query_string = {
        "sort": {
            "@timestamp": "desc"
        },
        "from": 0,
        "size": 1000,
        "query": {
            "bool": {
                "filter":
                    {"range": {"@timestamp": {"time_zone": "+00:00", "gte": start_time, "lte": end_time}}}
            }
        }
    }

    query_string["query"]["bool"]["must"] = []

    if service:
        query_string["query"]["bool"]["must"].append({"term": {"kubernetes.labels.app.keyword": service}})

    if keyword:
        keyword = keyword.split(' ')
        for word in keyword:
            query_string["query"]["bool"]["must"].append({"match": {"log": word}})

    if not keyword and not service:
        query_string["query"] = {
            "match_all": {}
        }

    records = []
    indices = query.get_queryable_indices(start_time=start_time, end_time=end_time)
    for index in indices:
        res = es.search(index=index, body=query_string)
        for item in res['hits']['hits']:
            records.append(item)
    return records