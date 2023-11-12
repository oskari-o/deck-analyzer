# Template for the final summary format
def default_summary_template():
    return """\
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

Product & Business model:

Unique Selling Proposition:

Market & Competition:
(Size if estimated)
(Competitors if known)

Customers & sales:

Product maturity & Roadmap:

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

# Template for the summary prompt
def get_summary_prompt_template(summary_template):
    prompt_template = """
You are an expert in summarizing startup pitchdecks.
Your goal is to create a structured summary memo of a pitchdeck for VC evaluation.
Below you find a partial extraction of the original pitchdeck pdf text:
--------
{text}
--------

Include only info existing in the pitchdeck. Total output will be a list of important aspects of the startup company in question, very briefly in bullet points (no lenghty sentences), in the format of the following template:

SUMMARY FORMAT TEMPLATE

""" + summary_template
    
    return prompt_template

# Template for the refine prompt
def get_refine_prompt_template(summary_template):
    prompt_template = """
You are an expert in summarizing startup pitchdecks.
Your goal is to create a structured summary memo of a pitchdeck for VC evaluation.
We have provided an existing summary up to a certain point: 
--------
{existing_answer}
--------
Below you find a partial extraction of the original pitchdeck pdf text:
--------
{text}
--------
Given the new context, refine the summary if applicable. You can trust the existing summary information. If the context isn't useful, return the original summary.
Total output will be a list of important aspects of the startup company in question, very briefly in bullet points (no lenghty sentences), in the format of the following template.
If the existing summary doesn't yet follow the following template, change it to the following template:

SUMMARY FORMAT TEMPLATE
        
    """ + summary_template
    
    return prompt_template