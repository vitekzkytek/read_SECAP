from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DeepInfraEmbeddings
import os
from langchain_core.embeddings import Embeddings
from openai import OpenAI

class EmbeddingsModel(Embeddings):
    def __init__(
        self, 
        model,
        api_key=None, 
        base_url=None,
        batch_size=32
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url            
        )
        self.model = model
        self.batch_size = batch_size

    def embed_documents(self, texts):
        if not texts:
            return []
        
        # Split texts into batches
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Create embeddings for the current batch
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            # Extend embeddings list with current batch's embeddings
            embeddings.extend([data.embedding for data in response.data])
        
        return embeddings
    
    def embed_query(self, text):
        # Use the same method as embed_documents, but for a single text
        return self.embed_documents([text])[0]


def load_models(service='GPT@JRC'):
    if service == 'GPT@JRC':
        llm = ChatOpenAI(
            model="llama-3.3-70b-instruct",
            api_key=os.getenv('GPTJRC_API_TOKEN'),
            base_url=os.getenv('GPTJRC_BASE_URL'),
        )
        emb = EmbeddingsModel(
            model='multilingual-e5-large',
            api_key=os.getenv('GPTJRC_API_TOKEN'),
            base_url=os.getenv('GPTJRC_BASE_URL')
        )

    elif service == 'DeepInfra':
        llm = ChatOpenAI(
            model="meta-llama/Llama-3.3-70B-Instruct",
            api_key=os.getenv('DEEPINFRA_API_TOKEN'),
            base_url=os.getenv('DEEPINFRA_BASE_URL'),
        )

        emb = DeepInfraEmbeddings(
            model_id="intfloat/multilingual-e5-large"
        )

    else:
        raise ValueError('Unknown service ...')
    return llm, emb

