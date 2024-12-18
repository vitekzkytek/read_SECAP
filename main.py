from llm import load_models
from dotenv import load_dotenv
from questioning import load_qdf, ask_qs_using_RAG, pdf_to_documents, documents_to_vector_store
import os
from logging_config import logger


if __name__ == '__main__':
    load_dotenv()

    llm, emb = load_models(service = 'DeepInfra')

    qdf = load_qdf() # questions from JSON

    pdfs = [f for f in os.listdir('pdf_input') if f.endswith('.pdf')]
    for pdf in pdfs:
        logger.info(f'Starting PDF {pdf}')
        
        logger.debug('Reading the documents..')
        document, documents = pdf_to_documents(pdf)
        
        logger.debug('Converting to vector store ...')
        vector_store = documents_to_vector_store(documents, emb)

        ask_qs_using_RAG(
            qdf = qdf, 
            llm = llm, 
            vector_store = vector_store,
            pdf = f'pdf_input/{pdf}',
            output_json = 'output/qs_rag.json',
            logger=logger
        )
