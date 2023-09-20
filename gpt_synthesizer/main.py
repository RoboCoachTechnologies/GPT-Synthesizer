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
from ui import message_func, print_bot, print_user



def main(verbose = False):
    st.set_page_config(page_title="GPT Synthesizer", initial_sidebar_state='auto', menu_items=None)
    st.title("🚀🤖🧑‍💻GPT Synthesizer!!!")
    st.caption('Generate your code base on your task description and programming language!')

    #print_user("Hi!")
    print_bot("Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG)
    # print_user("Hi back!")
    # print_bot("you get the idea")

    INITIAL_MESSAGE = [
        {"role": "user", "content": "Hi!"},
        {
            "role": "assistant",
            "content": "Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG,
        },
    ]

    if "messages" not in st.session_state.keys():
        st.session_state["messages"] = INITIAL_MESSAGE

    # print_bot("here we go!")
    # for message in st.session_state.messages:
    #     message_func(
    #         message["content"],
    #         True if message["role"] == "user" else False
    #     )
    # print_user('we are done')
    if "history" not in st.session_state:
        st.session_state["history"] = []

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

    # Open the file in write mode
    if not os.path.exists('workspace'):
            os.mkdir(f'workspace')

    with open('workspace/terminal_log.log', 'w') as file:
        pass  # This will effectively erase the contents of the file

    logging.basicConfig(
        filename='workspace/terminal_log.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    llm = llm_init()

    comp_prompt, comp_parser = get_comp_prompt()
    comp_chain = LLMChain(
        llm=llm,
        prompt=comp_prompt,
        verbose=verbose
    )

    logging.info(ui.WELCOME_MSG)

    # task_message = input("Programming task: ")  # User-specified task
    print_bot('Programming task: ')
    if task_message := st.text_input('Programming task'):
        st.session_state.messages.append({"role": "user", "content": task_message})

    if task_message == '' or task_message == None:
        #st.warning("Please enter your programming task")
        st.stop()

    print_user(task_message)

    logging.info(f"Programming task: {task_message}")
    #message_func(task_message, True)


   

    print_bot('Programming language: ')
    if lang_message := st.text_input('Programming language'):
        st.session_state.messages.append({"role": "user", "content": lang_message})

    print('IM HERE')
    print(task_message)
    print(lang_message)
    if lang_message == '' or lang_message == None:
        #st.warning("Please enter your programming task")
        st.stop()

    print("IM HERE 2")
    print_user(lang_message)
    # lang_message = input("Programming language: ")  # User-specified language
    logging.info(f"Programming language: {lang_message}")

    comp_output = comp_chain.predict(input=task_message, lang=lang_message)
    comp_list = comp_parser.parse(comp_output).components

    comp_list_str = make_comp_list(comp_list)
    print("IM HERE 3")
    # print(ui.COMP_MSG_INIT)
    print_bot(ui.COMP_MSG_INIT)
    logging.info(ui.COMP_MSG_INIT)

    print_bot(comp_list_str)
    logging.info(comp_list_str)

    print_bot(ui.COMP_MSG_ADD)
    logging.info(ui.COMP_MSG_ADD)

    if add_comp_message := st.text_input("Components to be added: "):
        st.session_state.messages.append({"role": "user", "content": add_comp_message})
        logging.info(f"Components to be added: {add_comp_message}")

    if add_comp_message == '' or add_comp_message == None:
        #st.warning("Please enter your programming task")
        st.stop()

    if add_comp_message.lower().__contains__('none'):
        add_comp_message = ""   

    if len(add_comp_message) == 0:
        print_bot(ui.COMP_MSG_UPDATE_NO_ADD)
        logging.info(ui.COMP_MSG_UPDATE_NO_ADD)
    else:
        comp_list = extend_comp_list(comp_list, add_comp_message)
        comp_list_str = make_comp_list(comp_list)
        print_bot(ui.COMP_MSG_UPDATE_ADD)
        logging.info(ui.COMP_MSG_UPDATE_ADD)
        print_bot(comp_list_str)
        logging.info(comp_list_str)

    #print(ui.COMP_MSG_RM)
    print_bot(ui.COMP_MSG_RM)
    logging.info(ui.COMP_MSG_RM)

    if rm_comp_message := st.text_input("Components to be removed: "):
        logging.info(f"Components to be removed: {rm_comp_message}")

    if rm_comp_message == '' or rm_comp_message == None:
        #st.warning("Please enter your programming task")
        st.stop()

    if rm_comp_message.lower().__contains__('none'):
        rm_comp_message = ""

    comp_list = remove_comp_list(comp_list, rm_comp_message)
    comp_list_str = make_comp_list(comp_list)

    print_bot(ui.COMP_MSG_FINAL_1)
    logging.info(ui.COMP_MSG_FINAL_1)
    print_bot(comp_list_str)
    logging.info(comp_list_str)
    print_bot(ui.COMP_MSG_FINAL_2)
    logging.info(ui.COMP_MSG_FINAL_2)

    all_comps_1 = """"""
    all_comps_2_spec = """"""
    all_comps_2_func_list = """"""

    all_summary = ""
    counter = 0
    for comp in comp_list.keys():
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

        init_human_input = "I want to implement '{comp}'".format(comp=comp)
        spec_output = spec_chain.predict(input=init_human_input)

        print_bot(ui.SPEC_MSG_TITLE.format(comp=comp))
        logging.info(ui.SPEC_MSG_TITLE.format(comp=comp))
        print_bot(spec_output)
        logging.info(spec_output)
        while spec_end_str not in spec_output:
            if human_response := st.text_input(f"Answer {counter+1}: ", key=f"Answer {counter+1}"):
                logging.info(f"Answer: {human_response}")

            if human_response == '' or human_response == None:
                #st.warning("Please enter your programming task")
                st.stop()

            spec_output = spec_chain.predict(input=human_response)
            spec_output_clean = spec_output.replace(spec_end_str, "")
            print_bot(spec_output_clean)
            logging.info(spec_output_clean)
            counter += 1

        sum_prompt = get_summarize_prompt()
        summary_chain = LLMChain(
            llm=llm,
            prompt=sum_prompt,
            verbose=verbose
        )

        spec_memory.return_messages = True
        sum_output = summary_chain.predict(input=spec_memory.load_memory_variables({}))
        all_summary += sum_output

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

        code_generator(task_message, lang_message, comp, comp_list[comp],
                       generate_func_list_output, sum_output, llm, verbose)
        

        all_comps_1, all_comps_2_spec, all_comps_2_func_list = make_func_list(comp, comp_list[comp],
                                                                              generate_func_list_output,
                                                                              all_comps_1,
                                                                              all_comps_2_spec,
                                                                              all_comps_2_func_list)

    # Currenty implemented main generation for Python code
    if lang_message.lower().__contains__('python'):
        main_generator(task_message, lang_message, comp_list, all_summary, llm, verbose)

    print_bot(ui.FAREWELL_MSG)
    logging.info(ui.FAREWELL_MSG)
    logging.shutdown()


if __name__ == "__main__":
    main()