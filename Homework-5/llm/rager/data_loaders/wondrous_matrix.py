from typing import Dict, List, Union

import numpy as np
from elasticsearch import Elasticsearch

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def search(query_embedding: Union[List[int], np.ndarray], *args, **kwargs) -> List[Dict]:
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    index_name = kwargs.get('index_name', 'documents')
    source = kwargs.get('source', "cosineSimilarity(params.query_vector, 'embedding') + 1.0")
    top_k = kwargs.get('top_k', 5)
    chunk_column = kwargs.get('chunk_column', 'content')

    if isinstance(query_embedding, np.ndarray):
        query_embedding = query_embedding.tolist()

    query_object = []

    if query_embedding is not None:
        script_query = dict(
            script_score=dict(
                query=dict(match_all=dict()),
                script=dict(source=source, params=dict(query_vector=query_embedding)),
            )
        )
        query_object.append(script_query)

    text_query = "When is the next cohort?"

    if text_query:
        text_match_query = dict(
            match=dict(
                content=text_query
            )
        )
        query_object.append(text_match_query)

    combined_query = dict(
        bool=dict(
            should=query_object
        )
    )

    es_client = Elasticsearch(connection_string)

    response = es_client.search(
        index=index_name,
        query=dict(
            size=top_k,
            query=script_query,
            _source=[chunk_column],
        ),
    )

    return [hit['_source']['content'] for hit in response['hits']['hits']]


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'