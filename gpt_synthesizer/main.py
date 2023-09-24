# TODO: Remove print statements, experiment with messages state session versus print_bot, look into streamlit caching,  
import logging
import os
import streamlit as st

from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory

from gpt_synthesizer.model import llm_init
from gpt_synthesizer.prompt import get_comp_prompt, get_qa_prompt, get_summarize_prompt, get_generate_func_list_prompt
from gpt_synthesizer.parser import make_comp_list, extend_comp_list, remove_comp_list, make_func_list
from generate_code import code_generator
from generate_main import main_generator
import ui
from ui import print_bot, print_user

print('setting components and all summary to empty strings')
if 'init_components_bool' not in st.session_state.keys():
    st.session_state.all_comps_1 = """"""
    st.session_state.all_comps_2_spec = """"""
    st.session_state.all_comps_2_func_list = """"""
    st.session_state.all_summary = ""

all_comps_1 = st.session_state['all_comps_1']
all_comps_2_spec = st.session_state['all_comps_2_spec']
all_comps_2_func_list = st.session_state['all_comps_2_func_list']
all_summary = st.session_state['all_summary']

counter = 0
print("\nI'm at a global level and what to see if I get called! I am above the main function!")

def main(verbose = False):
    print('Setting up streamlit headers and first bot message')
    st.set_page_config(page_title="GPT Synthesizer", initial_sidebar_state='auto', menu_items=None)
    st.title("🚀🤖🧑‍💻GPT Synthesizer!!!")
    st.caption('Generate your code base on your task description and programming language!')
    print_bot("Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG)

    print("I am making the initial message!")
    INITIAL_MESSAGE = [
        {"role": "user", "content": "Hi!"},
        {
            "role": "assistant",
            "content": "Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG,
        },
    ]

    print("creating session keys 'messages' and 'history' if they don't exist")
    if "messages" not in st.session_state.keys():
        print("I am actually creating 'messages' ")
        st.session_state["messages"] = INITIAL_MESSAGE

    if "history" not in st.session_state:
        st.session_state["history"] = []
    
    # print_bot("here we go!")
    # for message in st.session_state.messages:
    #     message_func(
    #         message["content"],
    #         True if message["role"] == "user" else False
    #     )
    # print_user('we are done')


    print("I am making the sidebar")
    st.sidebar.title("Enter Your OpenAI API Key 🗝️")
    open_api_key = st.sidebar.text_input(
        "OpenAI API Key", 
        value=st.session_state.get('openai_api_key', ''),
        help="Get your API key from https://openai.com/",
        type='password'
    )

    print("I am checking the API key otherwise I am stopping and warning the user")
    if open_api_key == '':
        st.sidebar.warning("Please enter your OpenAI API key")
        st.stop()

    # TODO: REMOVE THIS LINE BEFORE COMMITTING
    print("I overwrote the API key with a hard coded one")


    print("making key an environment variable and session state variable")
    st.session_state['openai_api_key'] = openai_api_key

    openai_api_key = st.session_state['openai_api_key']
    os.environ["OPENAI_API_KEY"] = openai_api_key

    if 'workspace_bool' not in st.session_state.keys():
        st.session_state['workspace_bool'] = True
        print("setting up workspace folder")
        # Open the file in write mode
        if not os.path.exists('workspace'):
                os.mkdir(f'workspace')

    if 'log_bool' not in st.session_state.keys():
        st.session_state['log'] = True
        print("setting up terminal log by erasing its contents if exists and setting up config")
        with open('workspace/terminal_log.log', 'w') as file:
            print("I am erasing the terminal log file")
            pass  # This will effectively erase the contents of the file

    # TODO: CHECK IF THIS WELL PERSIST BETWEEN SESSIONS
    logging.basicConfig(
        filename='workspace/terminal_log.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if 'init_llm_bool' not in st.session_state.keys():
        st.session_state['init_llm_bool'] = True
        print("instantiating LLM model")
        st.session_state['llm'] = llm_init()

    llm = st.session_state['llm']

    if 'comp_prompt_parser_bool' not in st.session_state.keys():
        st.session_state['comp_prompt_parser_bool'] = True
        print("setting up the components prompt and parser")
        st.session_state.comp_prompt, st.session_state.comp_parser = get_comp_prompt()
        st.session_state.comp_chain = LLMChain(
            llm=llm,
            prompt=st.session_state.comp_prompt,
            verbose=verbose
        )
    comp_chain = st.session_state['comp_chain']
    comp_prompt, comp_parser = st.session_state.comp_prompt, st.session_state.comp_parser
    logging.info(ui.WELCOME_MSG)

    print_bot('Programming task: ')

    if 'task_message_bool' not in st.session_state.keys():
        print("I am asking user for their programming task")
        if task_message := st.text_input('Programming task'):
            st.session_state.messages.append({"role": "user", "content": task_message})

        print('checking if task message is empty')

        if task_message == '' or task_message == None:
            #st.warning("Please enter your programming task")
            st.stop()

        st.session_state['task_message_bool'] = True
        st.session_state['task_message'] = task_message
    
    task_message = st.session_state['task_message']

    print('displaying user programming task')
    print_user(task_message)
    logging.info(f"Programming task: {task_message}")

    print_bot('Programming language: ')

    if 'lang_message_bool' not in st.session_state.keys():
        print("I am asking user for their programming language")
        if lang_message := st.text_input('Programming language'):
            st.session_state.messages.append({"role": "user", "content": lang_message})
        
        print('checking if lang message is empty')
        if lang_message == '' or lang_message == None:
            #st.warning("Please enter your programming task")
            st.stop()
        
        st.session_state['lang_message_bool'] = True
        st.session_state['lang_message'] = lang_message

    lang_message = st.session_state['lang_message']
    print(f"current lang_message is {lang_message} and current task_message is {task_message}")

    print("displaying user's programming language")
    print_user(lang_message)
    logging.info(f"Programming language: {lang_message}")


    if 'comp_list_bool' not in st.session_state.keys():
        st.session_state['comp_list_bool'] = True
        print('predicting component output and parsing it to get a list of components')
        comp_output = comp_chain.predict(input=task_message, lang=lang_message)
        st.session_state.comp_list = comp_parser.parse(comp_output).components

        
        print("making component list and displaying it")
        st.session_state.comp_list_str = make_comp_list(st.session_state.comp_list)
    
    comp_list = st.session_state['comp_list']
    comp_list_str = st.session_state['comp_list_str']

    print_bot(ui.COMP_MSG_INIT)
    logging.info(ui.COMP_MSG_INIT)
    print_bot(comp_list_str)
    logging.info(comp_list_str)

    print("I am asking user if they want to add or remove components")
    print_bot(ui.COMP_MSG_ADD)
    logging.info(ui.COMP_MSG_ADD)

    if 'add_comp_message_bool' not in st.session_state.keys():
        print("text input for components to be added")
        if add_comp_message := st.text_input("Components to be added: "):
            st.session_state.messages.append({"role": "user", "content": add_comp_message})
            logging.info(f"Components to be added: {add_comp_message}")

        print('checking if add comp message is empty')
        if add_comp_message == '' or add_comp_message == None:
            #st.warning("Please enter your programming task")
            st.stop()

        st.session_state['add_comp_message_bool'] = True
        st.session_state['add_comp_message'] = add_comp_message


    print('checking if add comp message contains none')
    if st.session_state.add_comp_message.lower().__contains__('none'):
        st.session_state.add_comp_message = ""   
    
    add_comp_message = st.session_state['add_comp_message']


    print('extending component list with components to be added unless is none')
    if len(add_comp_message) == 0:
        print_bot(ui.COMP_MSG_UPDATE_NO_ADD)
        logging.info(ui.COMP_MSG_UPDATE_NO_ADD)
        st.session_state.comp_list_add = st.session_state.comp_list
        st.session_state.comp_list_str_add = st.session_state.comp_list_str
    else:
        st.session_state.comp_list_add = extend_comp_list(st.session_state.comp_list, add_comp_message)
        st.session_state.comp_list_str_add = make_comp_list(st.session_state.comp_list_add)
        print_bot(ui.COMP_MSG_UPDATE_ADD)
        logging.info(ui.COMP_MSG_UPDATE_ADD)
        print_bot(st.session_state.comp_list_str_add)
        logging.info(st.session_state.comp_list_str_add)

    comp_list = st.session_state['comp_list_add']
    comp_list_str = st.session_state['comp_list_str_add']


    print_bot(ui.COMP_MSG_RM)
    logging.info(ui.COMP_MSG_RM)

    if 'rm_comp_message_bool' not in st.session_state.keys():
        print("I am asking user if they want to remove components")
        print("text input for components to be removed")
        if rm_comp_message := st.text_input("Components to be removed: "):
            logging.info(f"Components to be removed: {rm_comp_message}")

        print('checking if rm comp message is empty')
        if rm_comp_message == '' or rm_comp_message == None:
            #st.warning("Please enter your programming task")
            st.stop()

        st.session_state['rm_comp_message_bool'] = True
        st.session_state['rm_comp_message'] = rm_comp_message

        print('checking if rm comp message contains none')
        if rm_comp_message.lower().__contains__('none'):
            rm_comp_message = ""
            st.session_state['rm_comp_message'] = rm_comp_message

        print('removing components from component list unless is none (no logic for utilizing none)')
        st.session_state.comp_list_rm = remove_comp_list(st.session_state.comp_list_add, rm_comp_message)
        st.session_state.comp_list_str_rm = make_comp_list(st.session_state.comp_list_rm)

    rm_comp_message = st.session_state['rm_comp_message']
    comp_list = st.session_state['comp_list_rm']
    comp_list_str = st.session_state['comp_list_str_rm']
    
    print("displaying final component list")
    print_bot(ui.COMP_MSG_FINAL_1)
    logging.info(ui.COMP_MSG_FINAL_1)
    print_bot(comp_list_str)
    logging.info(comp_list_str)
    print_bot(ui.COMP_MSG_FINAL_2)
    logging.info(ui.COMP_MSG_FINAL_2)

##########################################################################################################

    

    #counter = 0
    print("I'm about to enter the for loop and counter is equal to ", counter)
    for comp in comp_list.keys():
        print("I'm in the for loop and counter is equal to ", counter)
        print('current component is ', comp)
        print("getting spec prompt and end string")
        spec_prompt, spec_end_str = get_qa_prompt(
            task=task_message, lang=lang_message,
            all_comps_1=all_comps_1, all_comps_2=all_comps_2_spec,
            curr_comp=comp, curr_comp_desc=comp_list[comp])
        spec_memory = ConversationBufferMemory()
        spec_chain = ConversationChain(
            llm=llm,
            prompt=spec_prompt,
            memory=spec_memory,
            verbose=verbose)


        print('initializing human input to implement component')
        init_human_input = "I want to implement '{comp}'".format(comp=comp)
        spec_output = spec_chain.predict(input=init_human_input)

        print("printing bot and logging spec message title and spec output")
        print_bot(ui.SPEC_MSG_TITLE.format(comp=comp))
        logging.info(ui.SPEC_MSG_TITLE.format(comp=comp))
        print_bot(spec_output)
        logging.info(spec_output)

        print("I am about to enter the while loop and counter is equal to ", counter)
        while spec_end_str not in spec_output:
            print("I'm in the while loop and counter is equal to ", counter)
            print("I am asking user for their answer")
            if human_response := st.text_input(f"Answer {counter+1}: ", key=f"Answer {counter+1}"):
                logging.info(f"Answer: {human_response}")

            print('checking if human response is empty')
            if human_response == '' or human_response == None:
                #st.warning("Please enter your programming task")
                st.stop()

            print('passing user input into model and getting model output')
            spec_output = spec_chain.predict(input=human_response)
            spec_output_clean = spec_output.replace(spec_end_str, "")
            print_bot(spec_output_clean)
            logging.info(spec_output_clean)
            counter += 1

        print('I am imediaetly after the while loop and counter is equal to ', counter)
        print("getting summary prompt")
        sum_prompt = get_summarize_prompt()
        summary_chain = LLMChain(
            llm=llm,
            prompt=sum_prompt,
            verbose=verbose
        )

        print('accumulating all summary')
        spec_memory.return_messages = True
        sum_output = summary_chain.predict(input=spec_memory.load_memory_variables({}))
        all_summary += sum_output

        print('getting generate func list prompt')
        generate_func_list_prompt = get_generate_func_list_prompt(comp, comp_list[comp],
                                                                  all_comps_1, all_comps_2_func_list)
        generate_func_list_chain = LLMChain(
            llm=llm,
            prompt=generate_func_list_prompt,
            verbose=verbose
        )
        generate_func_list_output = generate_func_list_chain.predict(task=task_message,
                                                                     lang=lang_message,
                                                                     summary=sum_output)

        print('generating code')
        code_generator(task_message, lang_message, comp, comp_list[comp],
                       generate_func_list_output, sum_output, llm, verbose)
        
        print('making function list')
        all_comps_1, all_comps_2_spec, all_comps_2_func_list = make_func_list(comp, comp_list[comp],
                                                                              generate_func_list_output,
                                                                              all_comps_1,
                                                                              all_comps_2_spec,
                                                                              all_comps_2_func_list)

    # Currenty implemented main generation for Python code
    print('generating main function and just left for loop')
    if lang_message.lower().__contains__('python'):
        main_generator(task_message, lang_message, comp_list, all_summary, llm, verbose)

    print('printing farewell message and shutting down logging')
    print_bot(ui.FAREWELL_MSG)
    logging.info(ui.FAREWELL_MSG)
    logging.shutdown()


if __name__ == "__main__":
    print("I am right before the main function is called!")
    main()
    print("I am right after the main function is called!")