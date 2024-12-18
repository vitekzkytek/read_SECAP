import json
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from tqdm import tqdm
from prompts import PROMPTS
import os 
from json import JSONDecodeError

def load_qdf(json_path='questions.json'):
    with open(json_path,'r') as f:
        questions = json.load(f)
    return pd.concat([pd.DataFrame(questions[key]['questions']).assign(context=questions[key]['context']) for key in questions])

def ask_qdfs(qdf, pdf, llm, vector_store, logger):
    resps = [
            standard_RAG_question(qrow, vector_store, llm, pdf, logger=logger) 
            for qrow in tqdm(qdf.to_dict(orient='records'), desc='Questions')
        ]

    return pd.DataFrame([r for r in resps if r is not None])
    

def pdf_to_documents(pdf, chunk_size=1000, chunk_overlap=200):
    loader = PyPDFLoader(pdf)
    document = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )

    return document, text_splitter.split_documents(document)

def documents_to_vector_store(documents, emb):
    return FAISS.from_documents(documents, emb)

def search_similar(q, vector_store, k=10):
    return vector_store.similarity_search(q,k=10)

def ask_RAG(embed_query, vector_store, llm, logger, template_key, pdf, template_kwargs={}):
    logger.debug(f'Asking {embed_query}')
    try:
        candidates = search_similar(embed_query, vector_store)
    except Exception as e:
        raise(Exception(f'Cannot retrieve candidates from vector store. Reason: {str(e)}'))
    
    if template_key not in PROMPTS:
        raise(Exception('template_key {template_key} does not exist.'))
    else:
        template = PromptTemplate.from_template(PROMPTS[template_key])

    try:
        message = template.invoke({**{'candidates':candidates}, **template_kwargs})
    except KeyError as ke:
        raise
    
    response = llm.invoke(message)
    return response_to_dict(response, pdf, logger)

def response_to_dict(response, pdf, logger):
    try:
        d = json.loads(response.content)
        if type(d) == type({}):
            d['pdf'] = pdf
        else:
            for el in d:
                el['pdf'] = pdf
        return d
    except JSONDecodeError:
        logger.error(f'Incorrectly formatted response. PDF: {pdf}. Response: {response.content}')


def standard_RAG_question(qrow, vector_store, llm, pdf, logger):
    return ask_RAG(
        embed_query = f"Context: {qrow['question']}. Question: {qrow['question']}",
        vector_store = vector_store,
        llm = llm,
        logger = logger,
        template_key = 'question_prompt',
        pdf = pdf,
        template_kwargs = qrow
    )

def query_action_detail(action, template_key, llm, vector_store, logger, pdf):
    return ask_RAG(
        embed_query = action,
        vector_store = vector_store,
        llm = llm,
        logger = logger,
        template_key = template_key,
        pdf = pdf,
        template_kwargs = {'action':action}
    )

def ask_long_context(documents, llm, template_key):
    template = PromptTemplate.from_template(PROMPTS[template_key])

    message = template.invoke({
        "documents":documents
    })
    response = llm.invoke(message)

    return response ## Generalize? to also allow direct JSONs?

def query_action_list(llm, documents, page_start, page_end, logger):
    logger.debug('Retrieving list of actions')
    response = ask_long_context(
        llm=llm,
        documents = [doc for doc in documents if doc.metadata['page'] >=page_start and doc.metadata['page'] <= page_end],
        template_key='action_list_prompt'
    )

    return  response.content.split('\n')