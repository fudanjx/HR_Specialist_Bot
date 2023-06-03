from langchain.chat_models import ChatAnthropic
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from streamlit_callback import StreamlitCallbackHandler
import streamlit as st
# from dotenv import load_dotenv
import PyPDF2
import os
import anthropic

def open_file(filepath):
    with open(filepath, 'r') as infile:
        return infile.read()


# anthropic.api_key = open_file('../OpenAI/custom-knowledge-chatbot/Bot_Alex/data/anthropicapikey.txt')

# os.environ['ANTHROPIC_API_KEY'] = anthropic.api_key
# load_dotenv()


class Text_Expert:
    def __init__(self):
        self.system_prompt = self.get_system_prompt()

        self.user_prompt = HumanMessagePromptTemplate.from_template("{user_question}")

        full_prompt_template = ChatPromptTemplate.from_messages(
            [self.system_prompt, self.user_prompt]
        )

        self.chat = ChatAnthropic(model='claude-v1-100k', max_tokens_to_sample=512, streaming=True, callbacks=[StreamlitCallbackHandler()])

        self.chain = LLMChain(llm=self.chat, prompt=full_prompt_template)

    def get_system_prompt(self):
        system_prompt = """
        You are a expert in Human Resource Talent Search. 

        You are adept at reviewing candidate's profile and assess the suitability based on Job description.

        Please do not answer anything outside of the context.

        Please carefully review the Job Description to understand what the hiring manager want

        ### JOB DESCRIPTION
        {context_01}
        ### END OF JOB DESCRIPTION
        
        Then compare against the candidates' CV
        
        ### Candidates' CV
        {context_02}
        ### END OF Candidates' CV
                 
        Rank the candiates based on their overall suitabilities.
        Provide jusitification for your ranking, if applicable, but keep it very very brief
               
        
        """

        return SystemMessagePromptTemplate.from_template(system_prompt)

    def run_chain(self, language, context_01, context_02, question):
        return self.chain.run(
            language=language, context_01 = context_01 , context_02 =context_02, user_question=question
        )


def retrieve_pdf_text(pdf_file):

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()  

    return text

def retrieve_multi_pdf_text(pdf_files):
    text = ""
    for pdf_file in pdf_files:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()  

    return text


st.set_page_config(page_title="Alex HR Bot",page_icon="🥳")
# create a streamlit app
st.title("HR Talent Specialist Bot")
st.write("(You may refresh the page to start over)")
# st.text_input("Enter Anthropic API Key", type="password")
anthropic.api_key = st.text_input("###### Enter Anthropic API Key", type="password")
os.environ['ANTHROPIC_API_KEY']= anthropic.api_key

def jd_upload():
    # create a upload file widget for a pdf
    pdf_file_01 = st.file_uploader("###### Upload JD in PDF", type=["pdf"])

    # if a pdf file is uploaded
    if pdf_file_01:
        # retrieve the text from the pdf
        if "context_01" not in st.session_state:
            st.session_state.context_01 = retrieve_pdf_text(pdf_file_01)

    

def cv_upload():
    # create a upload file widget for a pdf
    pdf_file_02 = st.file_uploader("###### Upload candidate's CVs in PDF", type=["pdf"], accept_multiple_files=True)
    # if a pdf file is uploaded
    if pdf_file_02:
        # retrieve the text from the pdf
        if "context_02" not in st.session_state:
            st.session_state.context_02 = retrieve_multi_pdf_text(pdf_file_02)       

col1, col2 = st.columns([2,3])
with col1:
    jd_upload()
with col2:
    cv_upload()

if anthropic.api_key:


    # if there's context_01 & context_02, proceed
    if ("context_01" in st.session_state)&("context_02" in st.session_state):
        # create a text input widget for a question
        question = st.text_input("Ask a question")
    
    # if "Text_Expert" not in st.session_state:
    #     st.session_state.Text_Expert = Text_Expert() 

        # create a button to run the model
        if st.button("Run"):
            # run the model
            tx_expert = Text_Expert()
            bot_response = tx_expert.run_chain(
                'English', st.session_state.context_01, 
                    st.session_state.context_02, question)

            if "bot_response" not in st.session_state:
                st.session_state.bot_response = bot_response

            else:
                st.session_state.bot_response = bot_response

    # display the response
    # if "bot_response" in st.session_state:
        # st.write(st.session_state.bot_response)
else:
    pass
