from openai import OpenAI
from test_data.testDescription import get_test_description
import argparse
from tqdm import tqdm

verbose = False

def set_verbosity(level):
    global verbose
    verbose = level
    
def v_log(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

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

summary_template = """
Light memo: (Company name)

Stage: (Funding round)
Contact e.g. CEO:
Website: 
Pitch deck:
Deal Team: (Leave empty)
Date: (Leave empty)

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
(Who are the founders - Names & backgrounds)

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

def split_text(text, chunk_size=1500):
    # Split the text into chunks of 'chunk_size'
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def iteratively_summarize(text, initial_summary="", iter_callback=None): # Printing to be removed/adjusted
    chunks = split_text(text)
    current_summary = initial_summary
    n_chunks = len(chunks)
    client = OpenAI()
    total_cost = 0
    
    input_p1000_tokens = 0.03
    output_p1000_tokens = 0.06
    
    print(f"Processing {n_chunks} chunks...")
    
    progress_bar = tqdm(range(n_chunks))
    
    for i in range(n_chunks):
        if i == 0:
            prompt = initial_prompt(chunks[0], summary_template)
        else:
            prompt = refine_prompt(chunks[i], summary_template, current_summary)
            
        v_log(f"\nPrompt {i + 1}/{n_chunks}:\n{prompt}\n")
        
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0
        )
        v_log(completion)
        current_summary = completion.choices[0].message.content
        
        output_cost = completion.usage.completion_tokens * output_p1000_tokens / 1000
        input_cost = completion.usage.prompt_tokens * input_p1000_tokens / 1000
        total_cost += (output_cost + input_cost)
        v_log(f"\nCost so far: {total_cost:.3f}\n")
        
        if not iter_callback is None:
            iter_callback()
            
        progress_bar.update(1)
    
    progress_bar.close()

    return current_summary, total_cost


def main():
    parser = argparse.ArgumentParser(description='Process a Pitch Deck PDF file for summarization.')
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument('pdf_path', type=str, help='Path to the PDF file to be processed')
    args = parser.parse_args()

    set_verbosity(args.verbose)
    pdf_path = args.pdf_path
    
    from VisionAnalyzer import get_descriptions
    from ResponseParser import structurize_summary
    
    description_list, cost1 = get_descriptions(pdf_path)
    long_description = "\n".join(description_list)
    # cost1 = 0
    # long_description = get_test_description()
    summary, cost2 = iteratively_summarize(long_description)
    print(f"Final Summary:\n\n {summary}\n\nTotal cost: {(cost1 + cost2):.3f}")
    
    struct_summary, cost3 = structurize_summary(summary)
    for key, value in struct_summary.items():
        print(f"{key}: {value}\n")
    
    print(f"Total cost: {(cost1 + cost2 + cost3):.3f}")
    
if __name__ == "__main__":
    main()