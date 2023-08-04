from langchain.prompts.prompt import PromptTemplate
from gpt_synthesizer.parser import get_comp_parser, get_func_list_parser, get_func_desc_parser


def get_comp_prompt():
    template = """A human wants to write a software with the help of a super talented software engineer AI.
    
    The AI uses the input from the human as well as the specified programming language in order to identify the components needed for implementing the software.
    
    The AI's response should be high-level and there is no need to provide code snippets. Each identified component should be responsible for a part of the implementation.
    
    The AI generates the component names and component descriptions as a dictionary, where the names are dictionary keys and the descriptions are dictionary values.
    
    The components should be complementary to each other, and their description should indicate how each component is used by the other components.
    
    {format_instructions}
    
    Human: {input}
    Programming language: {lang}
    AI:"""
    parser = get_comp_parser()
    return PromptTemplate(template=template, input_variables=["input", "lang"],
                          partial_variables={"format_instructions": parser.get_format_instructions()}), parser


def get_qa_prompt(task, lang, all_comps_1, all_comps_2, curr_comp, curr_comp_desc):
    template = """A human wants to write a software with the help of a super talented software engineer AI.
    
    The human task and the programming language are listed below:
    - Human task: {task}
    - Programming language: {lang}
    
    {all_comps_1}
    
    Currently, the AI needs to only focus on '{curr_comp}' for the task. {all_comps_2}
    
    Here is a description of '{curr_comp}': {curr_comp_desc}.
    
    The AI uses the following conversation in order to design questions that identify the specifications for implementing '{curr_comp}'.

    The AI will continue asking questions until all the details for implementing '{curr_comp}' become clear. The AI will stop asking questions when it thinks there is no need for further clarification about '{curr_comp}'.
    
    The conversation should remain high-level and in the context of the human task. There is no need to provide code snippets. The AI should not generate messages on behalf of the human. The AI concludes the conversation by saying 'END_OF_SPEC'.

    Current conversation:
    {history}
    Human: {input}
    AI:"""
    return PromptTemplate(template=template,
                          input_variables=["history", "input"],
                          partial_variables={"task": task,
                                             "lang": lang,
                                             "all_comps_1": str(all_comps_1),
                                             "all_comps_2": str(all_comps_2),
                                             "curr_comp": curr_comp,
                                             "curr_comp_desc": curr_comp_desc}), "END_OF_SPEC"


def get_summarize_prompt():
    template = """The following is a conversation between an AI and a human regarding implementation of a software. Summarize the conversation in bullet point format by extracting the most important information exchanged within the conversation.
    
    Conversation:
    {input}"""
    return PromptTemplate(template=template, input_variables=["input"])


def get_short_sum_prompt():
    template = """The following is a conversation between an AI and a human regarding implementation of a software. 
    
    This conversation will be used by a programmer to write the code for the software.
    
    However, it needs to be summarized so it only contains the most important information related to the software implementation task.
    
    Extract the most important information in the conversation and summarize it in a single paragraph.

    Conversation:
    {input}"""
    return PromptTemplate(template=template, input_variables=["input"])


def get_generate_func_list_prompt(curr_comp, curr_comp_desc, all_comps_1, all_comps_2):
    template = """You are an advanced software programmer AI that implements code given a specific task and programming language by a user.

        User's task: {task} 
        Programming language: {lang}

        {all_comps_1}

        Your sole focus is generating a list of functions that implement '{curr_comp}' for the task. {all_comps_2}
        
        Here is a description of '{curr_comp}': {curr_comp_desc}.

        For additional information, here is a summary of a conversation between the user and another AI to further clarify how the user would like the code to be implemented. 

        Summary:
        {summary}

        Generate a list of functions needed for implementing '{curr_comp}' in {lang}.
        Think step by step and reason yourself to the right decisions to make sure we get it right.

        The generated list should be in the JSON format, containing `name` for function name, `description` for high-level function description, `inputs` as the list of inputs to the function, and `outputs` as the list of returned values.
        For example, the function `my_func()` should be described as follows:
        my_func():
            name: 'my_func'
            description: 'This function does some work'
            inputs: '[p_x, p_y, p_z]'
            outputs: '[o_x, o_y]'"""
    return PromptTemplate(template=template,
                          input_variables=["task", "lang", "summary"],
                          partial_variables={"curr_comp": curr_comp,
                                             "curr_comp_desc": curr_comp_desc,
                                             "all_comps_1": all_comps_1,
                                             "all_comps_2": all_comps_2.format(curr_comp=curr_comp)})


def get_generate_code_prompt():
    template = """You are an advanced software programmer AI that implements code given a specific task and programming language by a user.

        User's task: {task} 
        Programming language: {lang}

        The user's task is purely provided for context. Your sole focus is implementing '{curr_comp}'.
        
        Here is a description of '{curr_comp}': {curr_comp_desc}.
        
        Use the following list of functions for implementing '{curr_comp}'.
        
        {func_list}
        
        As you can see, each function has a name, a description, a list of inputs and outputs.
        
        Your implementation should follow the information provided in the above list. Keep in mind that your output will be ultimately utilized in the user's task.

        For additional information, here is a summary of a conversation between the user and another AI to further clarify how the user would like the code for '{curr_comp}' to be implemented. 

        Summary:
        {summary}

        Implement the code in {lang}. Make sure that you fully implement everything that is necessary for the code to work.
        Think step by step and reason yourself to the right decisions to make sure we get it right.

        Output your implementation strictly in the following format.

        FILENAME
        ```LANGUAGE
        CODE
        ```

        Where 'CODE' is your implementation, 'FILENAME' is '{curr_comp}' formatted to a valid file name, and 'LANGUAGE' is {lang}. 

        Please note that the code should be fully functional. No placeholders are allowed.
        Ensure to implement all code, if you are unsure, write a plausible implementation.
        Before you finish, double check that your implementation satisfies all of the specifications mentioned in the above summary."""
    return PromptTemplate(template=template,
                          input_variables=["task", "lang", "curr_comp", "curr_comp_desc", "func_list", "summary"])
