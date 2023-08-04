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

If the list is already complete or you want to remove some of the components, simply press ENTER.
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

Otherwise, simply press ENTER.
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

FAREWELL_MSG = """
It seems like we have implemented all the components. Farewell my friend!
"""
