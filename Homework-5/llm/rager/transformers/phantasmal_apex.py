if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import hashlib

@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block (expected to be a list of dictionaries)
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        A transformed list of documents with document IDs.
    """
    # Ensure data is a list
    if not isinstance(data, list):
        raise TypeError('Expected data to be a list of dictionaries.')

    documents = []

    for item in data:
        if not isinstance(item, dict):
            raise TypeError('Each item in data should be a dictionary.')
        
        # Check if 'documents' key exists in the dictionary
        if 'documents' not in item or 'course' not in item:
            raise KeyError('Each dictionary must contain "documents" and "course" keys.')

        doc = item['documents']
        doc['course'] = item['course']
        
        # Generate a document ID
        doc['document_id'] = generate_document_id(doc)
        documents.append(doc)

    return documents


def generate_document_id(doc):
    """
    Generate a unique document ID based on the course, question, and text content.
    """
    combined = f"{doc['course']}-{doc.get('question', '')}-{doc.get('text', '')[:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, list), 'The output should be a list'
    assert all(isinstance(doc, dict) for doc in output), 'Each item in the output should be a dictionary'
    assert all('document_id' in doc for doc in output), 'Each dictionary should contain a document_id'
