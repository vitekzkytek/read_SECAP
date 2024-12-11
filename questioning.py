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

def ask_qs_using_RAG(qdf, pdf, llm, emb, output_json,logger):
    logger.debug('Reading the documents..')
    documents = pdf_to_documents(pdf)
    logger.debug('Converting to vector store ...')
    vector_store = documents_to_vector_store(documents, emb)

    outputs = []

    for qrow in tqdm(qdf.to_dict(orient='records'), desc=pdf):
        candidates = search_similar(qrow['question'], vector_store)
        d = ask_RAG_question(qrow, candidates, llm, pdf, logger=logger)
        append_to_json(output_json, d)
    return outputs
    

def pdf_to_documents(pdf, chunk_size=1000, chunk_overlap=200):
    loader = PyPDFLoader(pdf)
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )

    return text_splitter.split_documents(documents)

def documents_to_vector_store(documents, emb):
    return FAISS.from_documents(documents, emb)

def search_similar(q, vector_store, k=10):
    return vector_store.similarity_search(q,k=10)

def ask_RAG_question(qrow, candidates, llm, pdf,logger):
    try:  
        logger.debug(f'Asking {qrow["qid"]}')
        template = PromptTemplate.from_template(PROMPTS['question_prompt'])
        message = template.invoke({
            "qid": qrow['qid'],
            "question": qrow['question'],
            "candidates": candidates,
            "response_format": qrow['response_format'],
            "additional_context": qrow['additional_context']
        })
        logger.debug(f'Template and message generated. Invoking LLM')
        response = llm.invoke(message)
        logger.debug(f'Response received; Formatting to JSON')
        d = json.loads(response.content)
        d['pdf'] = pdf
        return d

    except JSONDecodeError:
        logger.error(f'Incorrectly formatted response. PDF: {pdf} - QID: {qrow['qid']}. Response: {response.content}')
    except Exception as e:
        logger.error(f'Unhandled error: {str(e)}')




def append_to_json(json_file, obj):
    if os.path.exists(json_file):
        # File exists, so append to existing data
        with open(json_file, 'r+') as file:
            try:
                # Read existing data
                data = json.load(file)
                
                # If data is not a list, convert it to a list
                if not isinstance(data, list):
                    data = [data]
                
                # Append new object
                data.append(obj)
                
                # Move file pointer to the beginning and overwrite
                file.seek(0)
                json.dump(data, file, indent=2)
                file.truncate()
            
            except json.JSONDecodeError:
                # File exists but is empty or invalid
                json.dump([obj], file, indent=2)
    
    else:
        # File doesn't exist, create new file with object
        with open(json_file, 'w') as file:
            json.dump([obj], file, indent=2)
    