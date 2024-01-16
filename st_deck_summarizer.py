import os

# dotenv
from dotenv import load_dotenv

# Tempfile
import tempfile

# Streamlit
import streamlit as st

# Langchain PyPDF
from langchain.document_loaders import PyPDFLoader

# Pandas
import pandas as pd

# Import custom templates
from prompt_templates.default_summary_template import default_summary_template

# Import vision analyzer module
from vision_analyzer import get_descriptions, get_pdf_page_count

# Import GPT-4 summarizer module
from gpt4_summarizer import iteratively_summarize, n_chunks

# Import response parser module
from response_parser import structurize_summary


def main():

    # Title, caption and PDF file uploader
    st.title("Pitchdeck :rainbow[Summarizer] 1.0 ✨")
    st.caption(
        "This app uses OpenAI's GPT-4 to summarize pitchdecks according to a given summary template. Copyright 2024.")
    api_key_holder = st.empty()
    api_key_input = None
    pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

    # Summary template input, default template is loaded from Templates.py
    summary_template = default_summary_template()
    summary_template_input = st.text_area(
        "Summary template", value=summary_template, height=500, max_chars=1500, placeholder="Enter a summary template")
    st.divider()
    summary_text = st.empty()

    # Initiate session state and input / display for API key
    load_dotenv()
    env_api_key = os.environ.get('OPENAI_API_KEY')

    if env_api_key is not None:
        st.session_state['api_key'] = env_api_key
        api_key_input = api_key_holder.text_input(
            "OpenAI API Key - Read from .env file", type="password", value=st.session_state['api_key'], disabled=True)
    else:
        if 'api_key' not in st.session_state:
            st.session_state['api_key'] = ''
        api_key_input = api_key_holder.text_input(
            "OpenAI API Key. :gray[*Read more [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key)*]", type="password", value=st.session_state['api_key'])

    # Initiate session state
    if 'summary' not in st.session_state:
        st.session_state['summary'] = ''
    if 'summary-json' not in st.session_state:
        st.session_state['summary-json'] = {}
    if 'summary-table-data' not in st.session_state:
        st.session_state['summary-table-data'] = {}
    if 'warning' not in st.session_state:
        st.session_state['warning'] = '', ''

    # If summary is not empty, display it, otherwise display placeholder
    if st.session_state['summary'] != '':
        summary_text.text_area(
            "**Summary**", value=st.session_state['summary'], height=1500, disabled=True)
    else:
        summary_text.text_area(
            "**Summary**", value="Summary will appear here", disabled=True)

    # Rest of the UI elements & holders, below the summary text
    summary_button_holder = st.empty()
    summary_button = summary_button_holder.button(
        'Generate Summary 🪄', disabled=True)
    use_vision = st.checkbox("Use GPT-4 Vision API (costs more)")
    restructure_button_holder = st.empty()
    restructure_button = None
    export_button_holder = st.empty()
    message_holder = st.empty()
    summary_table_holder = st.empty()

    # If warning exists, display it
    if st.session_state['warning'][0] != '':
        message_holder.warning(
            st.session_state['warning'][0], icon=st.session_state['warning'][1])

    # If structured summary exists, display it
    if st.session_state['summary-table-data'] != {}:
        summary_table_holder.table(pd.DataFrame(
            st.session_state['summary-table-data']))

    # If PDF file is uploaded, load it and split it into pages
    if pdf_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf_file.read())
            pdf_path = tmp_file.name

            summary_button_holder.empty()

            # Activate the summary button
            if st.session_state.summary == '':
                summary_button = summary_button_holder.button(
                    'Generate Summary 🪄', key=1)
            else:
                summary_button = summary_button_holder.button(
                    'Re-generate Summary 🪄', key=2)

    # Main block: If summary button is pressed, generate the summary
    if summary_button:
        # Use the summary template from the input
        if summary_template_input is not None:
            summary_template = summary_template_input

        # Check & store the API key in session state
        if api_key_input is not "":
            if len(api_key_input) < 30 or len(api_key) > 100:
                st.session_state['warning'] = "Invalid API key format. Please enter a valid API key.", "⚠️"
                st.rerun()
            else:
                st.session_state['api_key'] = api_key_input
        else:
            st.session_state["warning"] = "No API key provided. Please enter an API key.", "⚠️"
            st.rerun()

        # Empty message & warning state
        st.session_state['warning'] = '', ''
        message_holder.empty()
        
        cost_descriptions = 0

        # UsePyPDF or Vision to get text from slides
        if not use_vision:
            # Use basic PyPDF from Langchain to get text from slides
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            combined_content = ''.join([p.page_content for p in pages])
        else:
            #Indicate page count
            n_pages = get_pdf_page_count(pdf_path)
            message_holder.info(
                f"Generating descriptions with GPT-4 Vision for {n_pages} pages...", icon="📷")

            # Use VisionAnalyzer to get descriptions of slides
            with st.spinner("Working..."):
                descriptions, cost_descriptions = get_descriptions(
                    pdf_path, delete_temp_files=True, api_key=st.session_state['api_key'])

            # If the descriptions didn't finish, display a warning
            if descriptions == []:
                st.session_state['warning'] = "Description generation with vision didn't finish. Check connection and try again.", "⚠️"
                st.rerun()
            else:
                message_holder.empty()
                combined_content = "\n\n".join(descriptions)

        # Indicate the number of steps for summarization
        steps_n = n_chunks(combined_content)
        message_holder.info(
            f"Generating summary in {steps_n} steps...", icon="📝")
        summary_button_holder.empty()

        # Generate the summary
        with st.spinner("Working..."):
            summary, cost_summary, finished = iteratively_summarize(
                combined_content, summary_template=summary_template, api_key=st.session_state['api_key'])

        # If the summary didn't finish, display a warning
        # TODO: Add a button to rerun from the last step
        if not finished:
            st.session_state['warning'] = "Summary generation didn't finish. Check connection and try again.", "⚠️"
            st.rerun()
        else:
            message_holder.empty()

        # Display the summary as a new text area
        summary_text.text_area(
            "**Summary**", value=summary, height=1500, disabled=True)

        # Store the summary in session state
        st.session_state.summary = summary
        
        # Display cost
        message_holder.success(
            f"Summary generated. Total cost: {cost_descriptions + cost_summary:.3f}$ (approx.)", icon="✅")

        # Re-activate the summary button
        summary_button = summary_button_holder.button(
            'Re-generate Summary 🪄', key=3)

    # If summary generated, display export button & restructure button
    # Currently disabled as the export function is WIP
    if st.session_state.summary != '':
        export_button = export_button_holder.button(
            'Export Summary to Google Drive 📁', disabled=True)
        restructure_button = restructure_button_holder.button(
            'Extract headings and values ⛏️')

    # If restructure button is pressed, parse the summary and display it as a table
    if restructure_button:
        # Indicate started processing
        message_holder.info("Processing summary in 1 step", icon="⛏️")
        
        # Parse the summary
        with st.spinner("Working..."):
            structured_summary, cost = structurize_summary(
                st.session_state.summary, api_key=st.session_state['api_key'])
        message_holder.empty()

        # Store structured summary in session state
        st.session_state['summary-json'] = structured_summary

        # Flip structure to table format
        data = {"Heading": structured_summary.keys(), "Text": structured_summary.values()}
        st.session_state['summary-table-data'] = data

        # Display the summary as a table
        structured_summary_df = pd.DataFrame(data)
        summary_table_holder.table(structured_summary_df)

        # Disable the restructure button
        restructure_button_holder.button(
            'Extract headings and values ⛏️', disabled=True, key=4)

    # If export button is pressed, export the summary to Google Drive with drive_export.py
    # if export_button:

    #     message_holder.info("Exporting to Google Drive...", icon="📁")

    #     print("\n\nStarting to Parse")

    #     #parsed = parse_summary(st.session_state.summary) # To Do error handling
    #     st.session_state['summary-json'] = parsed

    #     print("\n\nStarting to Export")

    #     file_name = export_to_drive(parsed) # To Do error handling

    #     message_holder.empty()
    #     message_holder.success(f"Exported to Google Drive as: {file_name}", icon="✅")


if __name__ == "__main__":
    main()
