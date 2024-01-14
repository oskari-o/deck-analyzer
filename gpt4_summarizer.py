from openai import OpenAI
import os
from dotenv import load_dotenv
import argparse
from tqdm import tqdm
from math import ceil

from vision_analyzer import get_descriptions
from response_parser import structurize_summary
from prompt_templates.iteration_prompts import initial_prompt, refine_prompt
from prompt_templates.default_summary_template import default_summary_template

verbose = False

def set_verbosity(level):
    global verbose
    verbose = level
    
def v_log(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

def n_chunks(text, chunk_size=1500):
    return ceil(len(text) / chunk_size)

def split_text(text, chunk_size=1500):
    # Split the text into chunks of 'chunk_size'
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Printing to be adjusted
# Important: Make a separate exported function that splits the chunks
def iteratively_summarize(text, initial_summary="", iter_callback=None, summary_template=default_summary_template(), api_key=None):
    chunks = split_text(text)
    current_summary = initial_summary
    n_chunks = len(chunks)
    
    if api_key is None:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    
    client = OpenAI(api_key=api_key)
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
    
    def range_limited_float_type(arg):
        """ Type function for argparse - a float within 0.0 - 1.0 """
        try:
            f = float(arg)
        except ValueError:    
            raise argparse.ArgumentTypeError("Must be a floating point number")
        if f < 0.0 or f > 1.0:
            raise argparse.ArgumentTypeError("Argument must be < 1.0 and > 0.0")
        return f
    
    parser = argparse.ArgumentParser(description='Process a Pitch Deck PDF file for summarization.')
    
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("-z", "--zoom", type=range_limited_float_type, default=1.0, help="Zoom factor for PDF to JPEG conversion - 1 is original size, 0.5 is half resolution")
    parser.add_argument('pdf_path', type=str, help='Path to the PDF file to be processed')
    args = parser.parse_args()

    set_verbosity(args.verbose)
    pdf_path = args.pdf_path
    
    description_list, cost1 = get_descriptions(pdf_path, zoom_factor=args.zoom)
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