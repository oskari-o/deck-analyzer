# Pitch Deck Summary App

## Introduction
The PitchDeck Summary App is a Streamlit-based application that uses OpenAI's GPT-4 to summarize pitch decks. It is designed to provide quick and efficient summaries based on a user-provided template and supports the processing of PDF files. Additionally, it can utilize the GPT-4 Vision API for enhanced functionality.

### ⚠️ Note ⚠️

This application is a prototype and is intended for proof-of-concept demonstration purposes. It incurs costs according to the OpenAI api pricing. Check pricing beforehand for vision preview and GPT-4 turbo. Decks larger than ~5MB per page will not work (that's very large). As a rule of thumb, a typical deck of 3MB and 10 pages will cost around 0.8$ with vision preview (Jan 2024). Please use responsibly
## Features
- **PDF Upload**: Users can upload pitch deck files in PDF format.
- **Custom Summary Templates**: Allows for input of a summary template to guide the summarization process.
- **GPT-4 Vision API Integration**: Option to use the GPT-4 Vision API for a more comprehensive analysis (note: this feature incurs additional costs).
- **Interactive Summarization**: Generates summaries interactively and displays them in the application.
- **Data Structuring**: Functionality to extract headings and values from summaries and display them in a tabular format.

## Live Demo
The application is hosted at: [TBD](TBD)

## Local Setup and Installation
To run this application locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/oskari-o/deck-analyzer
2. **Navigate to the Project Directory**:
   ```bash
   cd path/to/project
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
4. *Optional: Store OpenAI Api key in .env file in the root directory* 
   ```.env
   OPENAI_API_KEY=your_api_key_here
5. **Run the Application**:
   ```bash
   streamlit run st_deck_summarizer.py

## Application Logic
... TBD ...

### License: MIT
   
