from llm import load_models
from dotenv import load_dotenv
from questioning import load_qdf, ask_qs_using_RAG
import os
from logging_config import logger


if __name__ == '__main__':
    load_dotenv()

    llm, emb = load_models(service = 'DeepInfra')

    qdf = load_qdf()

    pdfs = [f for f in os.listdir('pdf_input') if f.endswith('.pdf')]
    for pdf in pdfs:
        logger.info(f'Starting PDF {pdf}')
        ask_qs_using_RAG(
            qdf = qdf, 
            llm = llm, 
            emb = emb,
            pdf = f'pdf_input/{pdf}',
            output_json = 'output/qs_rag.json',
            logger=logger
        )
