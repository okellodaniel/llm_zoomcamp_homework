if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import io
import requests
import docx


@data_loader
def load_data(*args, **kwargs):
    url = 'https://docs.google.com/document/d/1m2KexowAXTmexfC5rVTCSnaShvdUQ8Ag2IEiwBDHxN0/export?format=docx'
    
    doc = download_and_parse_doc(url)
    
    questions = extract_questions_from_doc(doc)

    documents = [
        {
            'course': 'llm-zoomcamp',
            'documents': question
        } for question in questions
    ]
    
    return documents


def download_and_parse_doc(url):
    """
    Downloads and parses the DOCX file from the given URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with io.BytesIO(response.content) as f_in:
            return docx.Document(f_in)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download the document: {e}")


def extract_questions_from_doc(doc):
    """
    Extracts questions and answers from the DOCX document.
    """
    questions = []

    question_heading_style = 'heading 2'
    section_heading_style = 'heading 1'

    current_section = ''
    current_question = ''
    current_answer = []

    for p in doc.paragraphs:
        style = p.style.name.lower()
        p_text = clean_line(p.text)

        if not p_text:
            continue

        if style == section_heading_style:
            current_section = p_text
        elif style == question_heading_style:
            # Store the previous question and answer
            if current_question and current_answer:
                questions.append({
                    'text': "\n".join(current_answer).strip(),
                    'section': current_section,
                    'question': current_question,
                })
                current_answer = []
            current_question = p_text
        else:
            current_answer.append(p_text)

    # Add the last question and answer
    if current_question and current_answer:
        questions.append({
            'text': "\n".join(current_answer).strip(),
            'section': current_section,
            'question': current_question,
        })

    return questions


def clean_line(line):
    """
    Cleans up a line of text by stripping whitespace and special characters.
    """
    return line.strip().strip('\uFEFF')


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, list), 'The output should be a list'
    assert all(isinstance(doc, dict) for doc in output), 'Each item in the output should be a dictionary'
