import re
from openai import OpenAI

def structurize_summary(summary):

  client = OpenAI()

  input_p1000_tokens = 0.03
  output_p1000_tokens = 0.06

  prompt = f"""
Provide a complete list of all the headings present in the following text,
in the order in which they appear, delimited by a newline and semicolon,
like the exaple below. Do not return anything else than the list of headings:

Example output:

---

Light memo;
Stage;
Website;
...
Problem;
...
Deal Structure & Terms;

---

Text to extract headings from:

---
{summary}
"""
  print(f"{prompt}\n\n")
  
  completion = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "system", "content": prompt}],
    temperature=0
  )

  headings = completion.choices[0].message.content
  sep_headings = [value.strip().strip(";") for value in headings.split(';\n')]
        
  output_cost = completion.usage.completion_tokens * output_p1000_tokens / 1000
  input_cost = completion.usage.prompt_tokens * input_p1000_tokens / 1000
  total_cost = (output_cost + input_cost)
  
  print(f"{sep_headings}\nCost so far: {total_cost:.3f}\n")
  
  structured_summary = {}
  
  for i, heading in enumerate(sep_headings):
    # Next heading or end of text
    next_heading = sep_headings[i + 1] if i + 1 < len(sep_headings) else None
    if next_heading:
      pattern = rf"{re.escape(heading)}(.*?)(?=\n{re.escape(next_heading)})"
    else:
      pattern = rf"{re.escape(heading)}(.*)" # Last heading
    # Regex pattern
    match = re.search(pattern, summary, re.DOTALL)
    if match:
      structured_summary[heading] = match.group(1).strip().strip(':').strip()
    else:
      structured_summary[heading] = ""
        
  print(structured_summary)
  
  return structured_summary, total_cost
  
def main():
  from test_data.testSummary import test_summary_3
  structurize_summary(test_summary_3())
  
if __name__ == "__main__":
  main()