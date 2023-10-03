import html
import re

import streamlit as st


WELCOME_MSG = """
Welcome! I am here to assist you with your programming task.

First, please briefly tell me what you would like to implement. Don't worry about the details! We will talk about them later.
"""

COMP_MSG_INIT = """
I see! Based on my knowledge, you might need the following components for your software:
"""

COMP_MSG_ADD = """
If you think I have missed some of the components, please let me know. You can add new components by telling me the names and their description in quotation marks.

Example: \"Add 'component 1: what component 1 does', 'component 2: what component 2 does', and 'component 3: what component 3 does' to the list of components.\"

If the list is already complete or you want to remove some of the components, simply type 'None'.
"""

COMP_MSG_UPDATE_ADD = """
Got it! Here is the updated list of the components after adding your suggestions:
"""

COMP_MSG_UPDATE_NO_ADD = """
Got it! I will not add any additional components to the above list.
"""

COMP_MSG_RM = """
If you want to remove components from the list, simply tell me the names in quotation marks.

Example: \"Remove 'component 1' and 'component 2' from the list of components.\"

Otherwise, simply type 'None'.
"""

COMP_MSG_FINAL_1 = """
Alright! Here is the final list of the components:
"""

COMP_MSG_FINAL_2 = """
Now I am going to ask some questions about the details for each of the components. Your answers will help me to better understand the specifications of the problem you are working on.
"""

SPEC_MSG_TITLE = """
Let's talk about {comp}.
"""

SPEC_MSG_END = """
Based on our conversation, I'm going to implement {comp}.
"""

GEN_CODE_MSG = """
I finished implementation for {comp}. You can find it in the 'workspace' directory.
"""

GEN_MAIN_MSG = """
I finished implementation the 'main' file. You can find it in the 'workspace' directory.
"""

FAREWELL_MSG = """
It seems like we have implemented all the components. Farewell my friend!
"""


def format_message(text):
    """
    This function is used to format the messages in the chatbot UI.

    Parameters:
    text (str): The text to be formatted.
    """
    text_blocks = re.split(r"```[\s\S]*?```", text)
    code_blocks = re.findall(r"```([\s\S]*?)```", text)

    text_blocks = [html.escape(block) for block in text_blocks]

    formatted_text = ""
    for i in range(len(text_blocks)):
        formatted_text += text_blocks[i].replace("\n", "<br>")
        if i < len(code_blocks):
            formatted_text += f'<pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{html.escape(code_blocks[i])}</code></pre>'

    return formatted_text


def print_user(text):
    avatar_url = "https://avataaars.io/?avatarStyle=Circle&topType=ShortHairShaggyMullet&accessoriesType=Prescription02&hairColor=Red&facialHairType=BeardMajestic&facialHairColor=BrownDark&clotheType=Hoodie&clotheColor=Red&eyeType=Default&eyebrowType=SadConcernedNatural&mouthType=Serious&skinColor=Pale"
    message_alignment = "flex-end"
    message_bg_color = "linear-gradient(135deg, #00B2FF 0%, #006AFF 100%)"
    avatar_class = "user-avatar"
    st.write(
        f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%; font-size: 14px;">
                    {text} \n </div>
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width: 50px; height: 50px;" />
            </div>
            """,
        unsafe_allow_html=True,
        )


def print_bot(text):
    avatar_url = 'https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Wayfarers&hairColor=BrownDark&facialHairType=Blank&clotheType=CollarSweater&clotheColor=Black&eyeType=Default&eyebrowType=Default&mouthType=Smile&skinColor=Pale'
    message_alignment = "flex-start"
    message_bg_color = "#EEEEEE"
    avatar_class = "bot-avatar"

    
    text = format_message(text)

    st.write(
        f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width: 50px; height: 50px;" />
                <div style="background: {message_bg_color}; color: black; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%; font-size: 14px;">
                    {text} \n </div>
            </div>
            """,
        unsafe_allow_html=True,
    )
