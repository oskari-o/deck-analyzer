def initial_prompt(chunk, summary_template):
    return f'''
You are an expert in summarizing startup pitchdecks according to a given template.
Your goal is to create a structured summary memo of a pitchdeck for VC evaluation, according to the given template.
Below you find a partial extraction of the original pitchdeck's description text, slide by slide:
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
Below you find a partial extraction of the original pitchdeck's description text, slide by slide:
--------
{chunk}
--------
Given the new context, refine the summary if applicable. You can trust the existing summary information. If the context isn't useful, return the original summary.
Total output will be a list of important aspects of the startup company in question, very briefly in bullet points (no lenghty sentences), in the format of the following template.
If the existing summary doesn't yet follow the following template, change it to the following template:

SUMMARY FORMAT TEMPLATE:

{summary_template}
'''
