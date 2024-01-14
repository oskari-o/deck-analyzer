import os
import base64
import time

import fitz
from PIL import Image
import io

import httpx
import asyncio
from tqdm.asyncio import tqdm

from prompt_templates.vision_prompt import default_vision_prompt as main_prompt

def get_pdf_page_count(pdf_path):
  pdf = fitz.open(pdf_path)
  page_count = len(pdf)
  pdf.close()
  return page_count

def convert_pdf_to_jpeg(pdf_path, zoom_factor=1, output_folder_path="temp"):
  # Open the PDF file
  pdf = fitz.open(pdf_path)

  files = []

  # Delete
  print(f'Number of pages: {len(pdf)}')

  for page_number in range(len(pdf)):
    # Get the page
    page = pdf.load_page(page_number)

    # Define the zoom factor for the resolution; lower values = lower resolution
    # A zoom factor of 1 is normal size, less than 1 is reduced size
    mat = fitz.Matrix(zoom_factor, zoom_factor)

    # Render page to an image (pix) object with the zoom factor
    pix = page.get_pixmap(matrix=mat)
    image_data = pix.tobytes("ppm")

    # Open the image using PIL
    image = Image.open(io.BytesIO(image_data))

    # Convert to JPEG
    jpeg_image = image.convert("RGB")

    filename = f"{output_folder_path}/page_{page_number + 1}.png"
    
    jpeg_image.save(filename, "PNG")
    files.append(filename)

  pdf.close()
  print("Finished converting PDF to PNG. File names:")
  print(files)
  return files


async def interpret_image(client, image_path, prompt, delete_file=False):

  # OpenAI API Key
  api_key = os.environ['OPENAI_API_KEY']

  # Function to encode the image
  def encode_image(image_path):
      with open(image_path, "rb") as image_file:
          return base64.b64encode(image_file.read()).decode('utf-8')

  # Getting the base64 string
  base64_image = encode_image(image_path)

  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }
  
  input_cost_per_1000_tokens = 0.01
  output_cost_per_1000_tokens = 0.03
  
  # Real API
  response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  
  if (response.status_code != 200):
    print(response.json())
    print(f"\nImage path: {image_path}\n")
    # Should raise an exception here
    
  # Delete temp file
  if delete_file:
    os.remove(image_path)
  
  total_cost = input_cost_per_1000_tokens / 1000 * response.json()["usage"]["prompt_tokens"] + output_cost_per_1000_tokens / 1000 * response.json()["usage"]["completion_tokens"]
  
  return response.json(), total_cost

async def process_pdf(pdf_path, prompt_per_page, zoom_factor=1, delete_temp_files=False):
  
  # Convert PDF to JPEG
  jpeg_paths = convert_pdf_to_jpeg(pdf_path, zoom_factor=zoom_factor)
  length = len(jpeg_paths)
  
  print(f'Processing {length} pages...')
  
  # Interpret each page
  async with httpx.AsyncClient(timeout = 40.0) as client:
    progress_bar = tqdm(range(length))
    
    async def interpret_and_update(i):
      time.sleep(i * 0.5 + 0.1)
      result = await interpret_image(client, jpeg_paths[i], prompt_per_page, delete_file=delete_temp_files)
      progress_bar.update(1)
      return result
    
    tasks = [interpret_and_update(i) for i in range(length)]
    results = await asyncio.gather(*tasks)
    progress_bar.close()
    
  descriptions = [f'Slide {i + 1}:\n{results[i][0]["choices"][0]["message"]["content"]}' for i in range(length)]
  total_cost = sum([result[1] for result in results])
  
  print(f'Finished processing {length} pages. Total cost: {total_cost}')
    
  return descriptions, total_cost

def get_descriptions(pdf_path, prompt_per_page=main_prompt, zoom_factor=1.0, delete_temp_files=False):
  descriptions, cost = asyncio.run(process_pdf(pdf_path, prompt_per_page, zoom_factor=zoom_factor, delete_temp_files=delete_temp_files))
  return descriptions, cost

# if __name__ == "__main__":
#   descriptions, cost = get_descriptions("test_data/test_deck.pdf")
#   print("\n\n".join(descriptions))
  
  
  