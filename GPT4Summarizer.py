import openai
from langchain.llms import OpenAI
import os
from test_data.testDescription import get_test_description
import json # Remove once not needed

def initial_prompt(chunk, summary_template):
    return f'''
    You are an expert in summarizing startup pitchdecks according to a given template.
    Your goal is to create a structured summary memo of a pitchdeck for VC evaluation, according to the given template.
    Below you find a partial extraction of the original pitchdeck pdf text:
    --------
    {chunk}
    --------

    Include only info existing in the pitchdeck. Total output will be a list of important aspects of the startup company in question, very briefly in bullet points (no lenghty sentences), in the format of the following template:

    SUMMARY FORMAT TEMPLATE:

    {summary_template}
    '''

def refine_prompt(chunk, summary_template, existing_summary):
    return f'''
    You are an expert in summarizing startup pitchdecks according to a given template.
    Your goal is to create a structured summary memo of a pitchdeck for VC evaluation, according to the given template.
    We have provided an existing summary up to a certain point: 
    --------
    {existing_summary}
    --------
    Below you find a partial extraction of the original pitchdeck pdf text:
    --------
    {chunk}
    --------
    Given the new context, refine the summary if applicable. You can trust the existing summary information. If the context isn't useful, return the original summary.
    Total output will be a list of important aspects of the startup company in question, very briefly in bullet points (no lenghty sentences), in the format of the following template.
    If the existing summary doesn't yet follow the following template, change it to the following template:

    SUMMARY FORMAT TEMPLATE:

    {summary_template}
    '''

summary_template = """
Light memo: Company name

Stage: (Funding round)
Contact e.g. CEO:
Website: 
Pitch deck:
Deal Team: (Leave empty)
Date: (Today's date)

Summary:
(here a short general summary of the company and the deal)

Problem:
(What problem is the company addressing)

Product & Business model:
(What is the main product, how is it priced and from whom)

Unique Selling Proposition:
(How does the company differentiate)

Market & Competition:
(Size if estimated)
(Competitors if known)

Customers & sales:
(Who are the customers, how many, how much revenue per customer)

Product maturity & Roadmap:
(State of the product, future plans)

Team & Management:
(Who are the founders)

Impact Assessment (Art. 9):

Investors & board:
(Existing investors if known)

Financials:
(Revenue now & projected if known)

Technology & IPs:

Regulatory risks/opportunities:

Deal structure & terms:
(Stage/funding volume/timeline)
(Participation / Lead / Syndication partners etc.)
"""

# Initialize OpenAI (GPT-4) with your API key
openai.api_key = os.environ['OPENAI_API_KEY']
llm = OpenAI(model_name="gpt-4", max_tokens=-1)

def split_text(text, chunk_size=1500):
    # Split the text into chunks of 'chunk_size'
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def iteratively_summarize(text, llm, initial_summary=""):
    chunks = split_text(text)
    current_summary = initial_summary
    n_chunks = len(chunks)

    for i in range(n_chunks):
        if i == 0:
            first_prompt = initial_prompt(chunks[0], summary_template)
            #completion = llm.generate([first_prompt], max_tokens=4000) # Some problem with this
            completion = llm.invoke(first_prompt)
            # current_summary = completion.choices[0].text.strip()
            # print(first_prompt)
            print(completion)
            print(json.dumps(completion, indent=4))
        # else:
        #     refine_prompt = refine_prompt(chunks[i], summary_template, current_summary)
        #     completion = llm.generate([refine_prompt], max_tokens=4000)
        #     current_summary = completion.choices[0].text.strip()
        #     print(refine_prompt)
        #     print(completion)

    return current_summary

# Example usage
long_text = get_test_description()
summary = iteratively_summarize(long_text, llm)
print("Final Summary:", summary)