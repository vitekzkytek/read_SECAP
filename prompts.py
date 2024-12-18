PROMPTS = {
  "question_prompt":'''
    Relevant pieces of the documents:
    {candidates}
    
    Question ID: {qid}
    Context: {context}
    Question: {question}
    Additional context: {additional_context}
    Response format: {response_format}

    Output structure: 
    ```json
    {{
        "qid":"QUESTION_ID",
        "question":"EXACT_QUESTION_PHRASING",
        "response":"RESPONSE_IN_APPROPRIATE_FORMAT",
        "explanation":"EXPLANATION_FOR_THE_GIVEN_QUESTION",
        "page_reference":"PAGE_NUMBER(S)_FROM_THE_DOCUMENT",
        "relevant_quotes":["EXACT_QUOTE_SUPPORTING_THE_ANSWER"]
    }}
    ```
    Do not use any other fields. Field names should always match the names above.

    Returned string always contain only the json. Do not use markdown code blocks. Returned string will always start with "{{" and end with "}}".

    Other common formatting issues to mind when formatting:
    - do not include trailing comma
    - multiple strings should always be surrounded list brackets "[" and "]"
  ''',

  "action_list_prompt":'''
    Full SECAP plan:

    {documents}

    Thoroughly review the entire SECAP plan above and meticulously collect ALL mitigation actions and measures described within it. It is crucial that you do not overlook or omit any action, no matter how small or seemingly insignificant. Be comprehensive and exhaustive in your collection.

    Be vigilant and thorough. Double-check your work to ensure you haven't missed any actions. Remember, completeness is key.

    Return the response in the a simple list of action titles (including its identifier or numbering if available), where each action is on separate line. 

    Remember: Your task is to capture EVERY SINGLE action or measure mentioned in the SECAP plan. Do not summarize or combine actions. Each distinct action, no matter how small, should be listed separately. Accuracy and completeness are paramount.
    Returned string always contain only the action titles. Do not use markdown code blocks.
  ''',
  "action_details": '''
I will provide you with an action title from the SECAP plan and you will some details:

    1. Action title in the original language (`action_title_orig_language`)
    2. Action title translated to English (`action_title_english`)
    3. A brief but informative description of the action in English (`action_description_english`)
    4. The exact page reference(s) where the action is described (`page_reference`)


You should also assign it to a set  of predefined categories. Also add details regarding the action impact 
and implementation in English (translate from the description in the document).

# The action: *{action}*

## Candidate documents containing a description:
{candidates}


## List of categories

### Policy sectors (multi-choice; field `sectors`)
- `municipal buildings`
- `residential buildings`
- `tertiary (non municipal) buildings, equipment/factilities`
- `transport`
- `industry`
- `local heat/cold production`
- `waste`
- `local electricity production`

### Policy areas (multi-choice; field `policy_areas`)
- `Agriculture and forestry related`
- `Electric vehicles`
- `Urban regeneration`
- `Cleaner efficient vehicles`
- `Modal shift to walking and cycling`
- `Hydroelectric power`
- `Integrated action`
- `Building envelope`
- `Car sharing pooling`
- `Information and communication technologies`
- `Tree planting in urban areas`
- `Behavioural changes`
- `Industry other`
- `Renewable energy for space heating and hot water`
- `Energy efficient lighting systems`
- `Energy efficiency in industrial processes`
- `Photovoltaics`
- `Energy efficient electrical appliances`
- `District heating cooling network`
- `Energy efficiency in space heating and hot water`
- `Combined heat and power`
- `Modal shift to public transport`
- `Waste and wastewater management`
- `Eco driving`
- `Improvement of logistics and urban freight transport`
- `Wind power`
- `Biomass power plant`
- `District heating cooling plant`
- `Energy efficiency in buildings`
- `Industry renewable energy`
- `Road network optimisation`
- `Mixed use development and sprawl containment`
- `Smart grids`
- `Waste & wastewater management`

### Policy instruments (multi-choice; field `policy_instruments`)
- `Land use planning`
- `Mobility planning regulation`
- `Energy management`
- `Awareness raising training`
- `Building standards`
- `Voluntary agreements with stakeholders`
- `Grants and subsidies`
- `Public procurement`
- `Energy certification labelling`
- `Third party financing`
- `Not applicable`
- `Road pricing`
- `Energy suppliers obligations`
- `Integrated ticketing and charging`
- `Energy carbon taxes`
- `Energy performance standards`

### Stakeholders (multi-choice; field `stakeholders`)
- `Citizens`
- `National government and/or agency(ies)`
- `Sub-national government(s) and/or agency(ies)`
- `Business and private sector`
- `NGOs & civil society`
- `Academia`
- `Education sector`
- `Trade unions`

### Financing source (multi-choice; field `financing_sources`)
- `Local authority's own resources`
- `EU funds and programmes`
- `National funds and programmes`
- `Regional funds and programmes`
- `Public-private partnerships`
- `Private partnerships`
- `Other`

### Implementation status (single choice; field `implementation_status`)
- `Not started`
- `Completed`
- `Cancelled`
- `Ongoing`
- `Postponed`

Always leave empty or missing value if you are not sure. Better safe than sorry.
Always use English here.

If not sure about the exact month of a start date use january. 
If not sure about the year, leave the field empty. 

In `impact_*` columns always include the reported unit. 
Do not attempt to convert the units.

{{
  "action":"<action-title>",
  "page_reference": "<PAGE_REFERENCE>",
  "title_english": "<ENGLISH_TRANSLATION_OF_TITLE>",
  "action_sectors": ["SECTOR1-LISTED-ABOVE","SECTOR2-LISTED-ABOVE"],
  "action_areas": ["AREA1-LISTED-ABOVE","AREA2-LISTED-ABOVE"],
  "action_policy_instruments": ["INSTRUMENT1-LISTED-ABOVE","INSTRUMENT2-LISTED-ABOVE"],
  "stakeholders": [
		  {{
		    "type": "&lt;STAKEHOLDER-TYPE-LISTED-ABOVE&gt;",
		    "should_be_involved": true/false,
		    "actually_involved": true/false,
		    "justification": "Brief explanation of why this stakeholder should or should not be involved, and whether they are actually involved"
		  }},
		  ...
		],
  "financing_sources": ["FINANCE-SOURCE-LISTED-ABOVE","FINANCE-SOURCE-LISTED-ABOVE"],
  "key_action": &lt;BOOL_INDICATING_LISTING_AS_KEY_ACTION&gt;,
  "implementation_status":"&lt;IMPLEMENTATION_STATUS_ABOVE&gt;",
  "detailed_description_english": "&lt;DETAILED DESCRIPTION IN ENGLISH&gt;",
  "responsible_department_organization": "&lt;DEPARTMENT OR ORGANIZATION RESPONSIBLE FOR IMPLEMENTATION&gt;",
  "impact_yearly_ghg_reduction": "&lt;ESTIMATION-OF-GREENHOUSE-GASES-IN-REPORTED-UNITS-OF-CO2-EQUIVALENTS-PER-YEAR &gt;",
  "impact_yearly_energy_savings":"&lt;ESTIMATED-YEARLY-ENERGY-SAVINGS-REPORTED UNITS-per year&gt;"
  "impact_renewable_energy_production": "&lt;ESTIMATED-PRODUCTION-REPORTED UNITS-per-year&gt;",
  "cost_estimation": {{
    "investment_costs": "&lt;TOTAL-INVESTMENTS-COSTS&gt;",
    "running_costs": "&lt;YEARLY-RUNNING-COSTS&gt;",
    "other_costs":""
  }},
  "timeframe_start": "&lt;START-DATE-IN-FORMAT MM/YYYY&gt;",
  "timeframe_end": "&lt;END-DATE-IN-FORMAT MM/YYYY&gt;",
  "implementation_status": "IMPLEMENTATION-STATUS-VALUE-LISTED-ABOVE",
  "social_aspects_discussed":true/false,
  "social_aspects_details":"details on social aspects considerations for the action"
}}

Returned string always contain only the json. Do not use markdown code blocks. Returned string will always start with "{{" and end with "}}"

Other common formatting issues to mind when formatting:
    - do not include trailing comma
    - multiple strings should always be surrounded list brackets "[" and "]"

''',

  "action_SMART": '''
The SMART criteria are often used to assess the efficient goal setting. 
Good objectives or goals should be SMART - Specific, Measurable, Assignable,
Realistic, and Time-bound.

Your task is to evaluate the SMARTness of the following action.

# Action Title: {action}

## Candidate documents describing the action: {candidates}

## SMART Criteria:

    **Specific (S)**: Clear, concise, and well-defined
    **Measurable (M)**: Quantifiable outcome with trackable progress
    **Achievable (A)**: Realistic and attainable with available resources and constraints
    **Relevant (R)**: Aligned with the overall goal and objective of the plan
    **Time-bound (T)**: Specific deadline or timeframe for completion

Using the SMART criteria, please provide a `score` for each letter 
(`S`, `M`, `A`, `R`, `T`) on a scale of 0-1, where 0 indicates the action does 
not meet the criteria and 1 indicates the action fully meets the criteria.
For each letter also add a very brief `explanation` of evaluation.

Evaluation Guidelines:

    Consider the action's clarity, concision, and definition
    Assess the action's measurability, including quantifiable outcomes and trackable progress
    Evaluate the action's achievability, including available resources and constraints
    Determine the action's relevance to the overall goal and objective of the plan
    Assess the action's time-bound nature, including specific deadlines or timeframes

Output Format:

Please return the results in the following JSON format:

{{
    "action":[action],
    "S": {{
      "score": [Score],
      "explanation": "[Explanation]"
    }},
    "M": {{
      "score": [Score],
      "explanation": "[Explanation]"
    }},
    "A": {{
      "score": [Score],
      "explanation": "[Explanation]"
    }},
    "R": {{
      "score": [Score],
      "explanation": "[Explanation]"
    }},
    "T": {{
      "score": [Score],
      "explanation": "[Explanation]"
    }}
}}

Returned string always contain only the json. Do not use markdown code blocks. Returned string will always start with "{{" and end with "}}".

Other common formatting issues to mind when formatting:
    - do not include trailing comma
    - multiple strings should always be surrounded list brackets "[" and "]"
''',
"barriers_prompt":'''
    Relevant pieces of the documents:
    {candidates}

    Task: List all barriers to accelerating emission reduction in view of the 2030 climate-neutrality goal that are explicitly described in the plan.
    For each barrier include:
      - `title`
      - `brief_description`
      - `page_reference`
      - `explanation`
      -  list with `category` (potentially multiple). Choose from the following categories: `Leadership`, `Financial`, `Regulatory`, `Operational`, `Organisational`, `Partnerships`, `Social`, `Environmental`, `Safety and Security`,  `Other`. 
        
    Response format: simple JSON using the fields above.

    Do not use any other fields. Field names should always match the names above.

    Returned string always contain only the json. Do not use markdown code blocks. Returned string will always start with "[" and end with "]"

    Other common formatting issues to mind when formatting:
    - do not include trailing comma
    - multiple strings should always be surrounded list brackets "[" and "]"

  ''',
  "participatory_processes":'''
    Relevant pieces of the documents:
    {candidates}

    Task: List all participatory processes described in the SECAP plan 
    For each barrier include:
      - `title`
      - `brief_description` - in English
      - `page_reference`
      - `explanation`
      - `relevant_stakeholders`: [{{"stakeholder":"<stakeholder-type>","role":"<ENGLISH-DESCRIPTION_OF_THEIR_ROLE>"}}, ...]
      - `implementation_barriers`:
      - `barriers_solution`
      - `citizen_contribution_clearly_defined`
        
    Response format: JSON using the fields above.

    Do not use any other fields. Field names should always match the names above.

    Returned string always contain only the json. Do not use markdown code blocks. Returned string will always start with "[" and end with "]"

    Other common formatting issues to mind when formatting:
    - do not include trailing comma
    - multiple strings should always be surrounded list brackets "[" and "]"
  '''
}