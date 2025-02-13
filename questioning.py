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
from time import sleep 
import re
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from openai import InternalServerError
from typing import Literal

def load_qdf(json_path='questions.json'):
    with open(json_path,'r') as f:
        questions = json.load(f)
    return pd.concat([pd.DataFrame(questions[key]['questions']).assign(context=questions[key]['context']) for key in questions])

def ask_qdfs(qdf, city, llm, vector_store, logger):
    resps = [
            standard_RAG_question(qrow, vector_store, llm, city, logger=logger) 
            for qrow in tqdm(qdf.to_dict(orient='records'), desc='Questions')
        ]

    return pd.DataFrame([r for r in resps if r is not None])
    
def pdfs_to_documents(pdfs=[]):
    all_documents = []
    all_splits = []
    
    for pdf in pdfs:
        doc, splits = pdf_to_documents(pdf)
        all_documents.extend(doc)
        all_splits.extend(splits)
        
    return all_documents, all_splits

def pdf_to_documents(pdf, chunk_size=1000, chunk_overlap=200):
    loader = PyPDFLoader(pdf)
    document = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        add_start_index=True
    )

    return document, text_splitter.split_documents(document)

def documents_to_vector_store(documents, emb):
    return FAISS.from_documents(documents, emb)

def search_similar(q, vector_store, k=10):
    return vector_store.similarity_search(q,k=10)

def ask_RAG(embed_query, vector_store, response_model, llm, logger, template_key, city, template_kwargs={},k=10):
    logger.debug(f'Asking {embed_query}')
    try:
        candidates = search_similar(embed_query, vector_store, k=k)
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
    try:
        response = invoke_pydantic(message, response_model, logger, llm)
    except Exception as e:
        raise(Exception(f'Cannot retrieve response from LLM. Reason: {str(e)}'))
    return response.model_dump()

def standard_RAG_question(qrow, vector_store, llm, city, logger):
    class StandardQuestion(BaseModel):
        qid: str = Field(..., description="Unique identifier for the question")
        question: str = Field(..., description="Exact wording of the question")
        response: str = Field(..., description="Response to the question in the appropriate format")
        explanation: str = Field(..., description="Explanation for the given response")
        page_reference: str = Field(..., description="Page number(s) from the document where the question is relevant")
        relevant_quotes: List[str] = Field([], description="Exact quotes supporting the answer")

    return ask_RAG(
        embed_query = f"Context: {qrow['context']}. Question: {qrow['question']}",
        vector_store = vector_store,
        response_model = StandardQuestion,
        llm = llm,
        logger = logger,
        template_key = 'question_prompt',
        city = city,
        template_kwargs = qrow
    )

def query_action_detail(action, llm, vector_store, logger, city):

    SectorType = Literal["municipal buildings", "residential buildings", "tertiary (non municipal) buildings, equipment/factilities", "transport",
        "industry", "local heat/cold production", "waste", "local electricity production"]

    PolicyAreaType = Literal[
        "Agriculture and forestry related", "Electric vehicles", "Urban regeneration","Cleaner efficient vehicles", "Modal shift to walking and cycling",
        "Hydroelectric power", "Integrated action", "Building envelope", "Car sharing pooling", "Information and communication technologies", "Tree planting in urban areas",
        "Behavioural changes", "Industry other", "Renewable energy for space heating and hot water", "Energy efficient lighting systems", "Energy efficiency in industrial processes",
        "Photovoltaics", "Energy efficient electrical appliances", "District heating cooling network", "Energy efficiency in space heating and hot water", "Combined heat and power",
        "Modal shift to public transport", "Waste and wastewater management", "Eco driving", "Improvement of logistics and urban freight transport", "Wind power", "Biomass power plant",
        "District heating cooling plant", "Energy efficiency in buildings", "Industry renewable energy", "Road network optimisation", "Mixed use development and sprawl containment", 
        "Smart grids","Waste & wastewater management"
    ]

    PolicyInstrumentType = Literal[
        "Land use planning", "Mobility planning regulation", "Energy management", "Awareness raising training", "Building standards", "Voluntary agreements with stakeholders",
        "Grants and subsidies", "Public procurement", "Energy certification labelling", "Third party financing", "Not applicable", "Road pricing", "Energy suppliers obligations",
        "Integrated ticketing and charging", "Energy carbon taxes", "Energy performance standards"
    ]

    StakeholderType = Literal[
        "Citizens", "National government and/or agency(ies)", "Sub-national government(s) and/or agency(ies)", "Business and private sector",
        "NGOs & civil society", "Academia", "Education sector", "Trade unions"
    ]

    FinancingSourceType = Literal[
        "Local authority's own resources", "EU funds and programmes", "National funds and programmes", "Regional funds and programmes", "Public-private partnerships", "Private partnerships", "Other"
    ]

    ImplementationStatusType = Literal[
        "Not started", "Completed", "Cancelled", "Ongoing", "Postponed"
    ]

    class Stakeholder(BaseModel):
        type: StakeholderType
        should_be_involved: bool
        actually_involved: bool
        justification: str

    class CostEstimation(BaseModel):
        investment_costs: str
        running_costs: str
        other_costs: Optional[str]

    class ActionModel(BaseModel):
        action: str
        page_reference: str
        title_english: str
        action_sectors: List[SectorType]
        action_areas: List[PolicyAreaType]
        action_policy_instruments: List[PolicyInstrumentType]
        stakeholders: List[Stakeholder]
        financing_sources: List[FinancingSourceType]
        key_action: bool
        implementation_status: ImplementationStatusType
        detailed_description_english: str
        responsible_department_organization: str
        impact_yearly_ghg_reduction: str
        impact_yearly_energy_savings: str
        impact_renewable_energy_production: str
        cost_estimation: CostEstimation
        timeframe_start: datetime
        timeframe_end: datetime
        social_aspects_discussed: bool
        social_aspects_details: Optional[str]

    return ask_RAG(
        embed_query = action,
        vector_store = vector_store,
        llm = llm,
        response_model = ActionModel,
        logger = logger,
        template_key = 'action_details',
        city = city,
        template_kwargs = {'action':action}
    )


def query_action_SMART(action, llm, vector_store, logger, city):

    class ScoreModel(BaseModel):
        """
        Model representing a score.
        """
        score: float = Field(..., description="List of scores. 1 means highest, 0 lowest", ge=0, le=1)
        explanation: str = Field(..., description="List of explanations")

    class SmartModel(BaseModel):
        """
        Model representing SMART evaluation of action.
        """
        action_title: str = Field(..., description="Action title")
        S: ScoreModel = Field(..., description="S score")
        M: ScoreModel = Field(..., description="M score")
        A: ScoreModel = Field(..., description="A score")
        R: ScoreModel = Field(..., description="R score")
        T: ScoreModel = Field(..., description="T score")
    
    return ask_RAG(
        embed_query = action,
        vector_store = vector_store,
        llm = llm,
        response_model = SmartModel,
        logger = logger,
        template_key = 'action_SMART',
        city = city,
        template_kwargs = {'action':action}
    )

def ask_long_context(documents, response_model, llm, template_key, logger):
    template = PromptTemplate.from_template(PROMPTS[template_key])

    message = template.invoke({
        "documents":documents
    })
    response = invoke_pydantic(message, response_model, logger, llm, original_prompt_in_clarification=False)
    return response


def query_action_list(llm, documents, logger):
    class Action(BaseModel):
        action_title_orig_language: str = Field(..., description="Action title in original language")
        action_title_english: str = Field(..., description="Action title in English")
        action_description: str = Field(..., description="Action description in English")
        page_reference: str = Field(..., description="Page reference")

    
    class ActionList(BaseModel):
        actions: List[Action] = Field(..., description="List of actions")

    logger.debug('Retrieving list of actions')
    try:
        response = ask_long_context(
            llm=llm,
            response_model= ActionList,
            documents = documents,
            template_key='action_list_prompt',
            logger=logger
        )

        return pd.DataFrame([action for action in response.model_dump()['actions']])
    except Exception as e:
        logger.error(f'Failed to retrieve list of actions: {str(e)}. Returning empty list of actions DataFrame')
        return pd.DataFrame(columns=list(Action.model_fields.keys()))

def filter_action_pages(documents, city_config):
    filtered_docs = []
    
    # Get PDFs config for the city
    pdfs_config = city_config['pdfs']
    
    for doc in documents:
        # Extract PDF filename from source
        doc_file = doc.metadata.get('source', '').split('/')[-1]
        
        # Find matching config for this document
        pdf_config = next((cfg for cfg in pdfs_config if cfg['file'] == doc_file), None)
        
        if pdf_config:
            start, end = pdf_config['action_page_limit']
            page_num = doc.metadata.get('page', 0)
            
            # Keep document if page is within limits
            if start <= page_num <= end:
                filtered_docs.append(doc)
                
    return filtered_docs

class LLMValidationError(Exception):
    pass

def invoke_pydantic(prompt, response_model, logger, llm, max_retries=5, retry_delay=1, original_prompt_in_clarification=True):
    response_succesful = False
    json_schema=response_model.model_json_schema()
    full_prompt = PROMPTS['pydantic_instructions'].format(
        original_prompt=prompt,
        json_schema=json_schema,
        formatting_requirements=PROMPTS['formatting_requirements']
    )
    processors = [
        lambda x: re.search(r"```json\n(.*?)\n```", x, re.DOTALL).group(1) 
                    if "```json" in x else x,
        lambda x: re.sub(r"^.*?(\{|\[)", r"\1", x, flags=re.DOTALL),
        lambda x: re.sub(r"(\}|\])[^}\]]*$", r"\1", x, flags=re.DOTALL)
    ]

    responses = []
    prompts = []

    for attempt in range(max_retries + 1):
        try:
            response = llm.invoke(full_prompt)
            content = response.content
            response_succesful = True
            
            # Apply response processors
            for processor in processors:
                try:
                    content = processor(content)
                except (AttributeError, IndexError):
                    continue
                    
            json_response = json.loads(content)
            return response_model.model_validate(json_response)
        except InternalServerError as e:
            if 'message' in e.body:
                if ('Requested input length' in e.body['message']) and ('exceeds maximum input length' in e.body['message']):
                    raise LLMValidationError(f"Input length exceeds maximum input length: {str(e)}. Consider limitting the input length for actions")

        except (JSONDecodeError, ValueError) as e:
            if attempt == max_retries:
                msg = f"Failed to get valid response after {max_retries} retries: {str(e)}"
                logger.error(
                    msg
                )
                print(prompts)
                print(responses)
                raise LLMValidationError(msg)
            if response_succesful:
                clarification_prompt = PROMPTS['pydantic_clarification'].format(
                    original_prompt=full_prompt if original_prompt_in_clarification else 'Sorry, original prompt is too long to display',
                    content=content,
                    error=str(e),
                    json_schema=json_schema,
                    formatting_requirements=PROMPTS['formatting_requirements']
                )
                sleep(retry_delay)
                full_prompt = clarification_prompt
                prompts.append(full_prompt)
                responses.append(content)
            else:
                logger.error(f"Failed to get response from LLM: {str(e)}")
                raise LLMValidationError(f"Failed to get response from LLM: {str(e)}")
