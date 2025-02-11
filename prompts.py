PROMPTS = {
  "question_prompt":'''
    Relevant pieces of the documents:
    {candidates}
    
    Question ID: {qid}
    Context: {context}
    Question: {question}
    Additional context: {additional_context}
    Response format: {response_format}
    ''',

  "action_list_prompt":'''
    Full SECAP plan:

    {documents}

    Thoroughly review the entire SECAP plan above and meticulously collect ALL mitigation actions and measures described within it.

    Extract all formally defined mitigation actions and measures that meet at least one of these criteria:
    - Listed under dedicated "Actions" or "Measures" sections
    - Often they have a distinct identifier or reference number
    - Contains specific targets, timelines, or resource allocations
    - Formally labeled as an action/measure/initiative
     
    Be vigilant and thorough. Double-check your work to ensure you haven't missed any actions. Remember, completeness is key.

    For each action return only basic set of information:
    - Action title both in original language of the plan and in English
    - Basic description of the action
    - page reference

    Remember: Your task is to capture EVERY SINGLE action or measure mentioned in the SECAP plan. Do not summarize or combine actions. Each distinct action, no matter how small, should be listed separately. Accuracy and completeness are paramount.
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

''',
"barriers_prompt":'''

    Context: Below are relevant excerpts from a Sustainable Energy and Climate Action Plan (SECAP).
    {candidates}
    
    Task: Analyze these excerpts and identify only explicitly stated barriers that affect the overall implementation 
    of the SECAP or achievement of emission reduction targets. 
    
    A barrier should be something that:
    1. Impedes the implementation of multiple actions or the plan as a whole
    2. Is clearly described using terms like "barrier", "challenge", "weakness", "lack of", etc.
    3. Is presented as a current or anticipated obstacle, not a hypothetical one
    
    If no clear barriers meeting these criteria are found, do not return any.
    ''',
  "participatory_processes":'''
  Context: Below are relevant excerpts from a Sustainable Energy and Climate Action Plan (SECAP).
  {candidates}

  Task: Analyze these excerpts for public participation elements. Structure your analysis into these categories:

  1. Formal Participation Processes
  - Include only concrete, implemented processes (not planned/proposed)
  - Quote relevant text as evidence

  2. Citizen Input Mechanisms
  - List specific tools/methods used to gather citizen input
  - Quote relevant text as evidence

  3. Stakeholder Groups
  - List only formally established groups
  - Quote relevant text as evidence

  4. Participation Barriers & Solutions
  - List only explicitly stated barriers/challenges
  - Include corresponding solutions if mentioned
  - Quote relevant text as evidence

  Do not infer or extrapolate beyond what is explicitly stated in the text. 
  Only include information that is directly supported by the excerpts.
  ''',
  "pydantic_instructions":'''
    {original_prompt}
  You must respond with a valid JSON object that matches this schema:
  {json_schema}

  {formatting_requirements}
  ''',
  "pydantic_clarification":'''
  Previous response was invalid.
  Original prompt: {original_prompt}
  Previous response: {content}
  Error: {error}
  Please provide response as JSON matching:
  {json_schema}

  Formatting requirements:
  {formatting_requirements}

  ''',
  "formatting_requirements":'''
  Formatting requirements:
  - Each action must be a complete object with all required fields. Do not return just identifiers or partial information.
  - Response must contain ONLY raw JSON
  - No markdown, no explanations
  - No trailing comma after last element
  - Use double quotes for strings
  - Escape only necessary special characters - mainly double quote (\") amd backslash (\\) with a single backslash ("\"). Do not use double backslashes ("\\"). Never escape single quotes ('), backtick (`) or tick (´).
  - Ensure all brackets and braces are correctly opened and closed
  '''
}