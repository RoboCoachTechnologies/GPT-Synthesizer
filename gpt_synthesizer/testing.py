import streamlit as st
import os
from ui import message_func
import gpt_synthesizer.ui as ui
from ui import message_func


st.set_page_config(page_title="GPT Synthesizer", initial_sidebar_state='auto', menu_items=None)
st.title("🚀🤖🧑‍💻GPT Synthesizer!!!")
st.caption('Generate your code base on your task description and programming language!')
model = "gpt-3.5-turbo-16k"
st.session_state['model'] = "gpt-3.5-turbo-16k"

st.sidebar.title("Enter Your API Key 🗝️")

open_api_key = st.sidebar.text_input(
    "Open API Key", 
    value=st.session_state.get('open_api_key', ''),
    help="Get your API key from https://openai.com/",
    type='password'
)

if open_api_key == '':
        st.sidebar.warning("Please enter your OpenAI API key")
        st.stop()

open_api_key = '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'

os.environ["OPENAI_API_KEY"] = open_api_key

st.session_state['open_api_key'] = open_api_key

INITIAL_MESSAGE = [
    {"role": "user", "content": "Hi!"},
    {
        "role": "assistant",
        "content": "Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!" + ui.WELCOME_MSG,
    },
]

if "messages" not in st.session_state.keys():
    st.session_state["messages"] = INITIAL_MESSAGE

if "history" not in st.session_state:
    st.session_state["history"] = []

if "model" not in st.session_state:
    st.session_state["model"] = model

# Prompt for user input and save
if prompt := st.chat_input(placeholder='Your response'):
    st.session_state.messages.append({"role": "user", "content": prompt})

st.text("some text")
#task messagst.text_input("What is the task you wish to accomplish?")






for message in st.session_state.messages:
    message_func(
        message["content"],
        True if message["role"] == "user" else False
    )
