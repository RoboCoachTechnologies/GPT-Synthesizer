# TODO: delay model instantiation until after task
import logging
import os
import streamlit as st

from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory

from gpt_synthesizer.model import llm_init
from gpt_synthesizer.prompt import get_comp_prompt, get_qa_prompt, get_summarize_prompt, get_generate_func_list_prompt
from gpt_synthesizer.parser import make_comp_list, extend_comp_list, remove_comp_list, make_func_list
from gpt_synthesizer.generate_code import code_generator
from gpt_synthesizer.generate_main import main_generator
import gpt_synthesizer.ui as ui
from gpt_synthesizer.ui import print_bot, print_user, GEN_CODE_MSG

program_options = ['Python', 'C++', 'Java', 'Swift', 'Other', '']
model_options = [':rainbow[GPT-3.5]', 'GPT-4']


def main(verbose = False):
    st.set_page_config(page_title="GPT Synthesizer", initial_sidebar_state='auto', menu_items=None)
    st.title("GPT Synthesizer")
    st.caption('Generate your code based on your task description and programming language!')
    print_bot("Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG)

    INITIAL_MESSAGE = [
        {"role": "user", "content": "Hi!"},
        {
            "role": "assistant",
            "content": "Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG,
        },
    ]

    if "messages" not in st.session_state.keys():
        st.session_state["messages"] = INITIAL_MESSAGE

    if "history" not in st.session_state:
        st.session_state["history"] = []
    
    st.sidebar.title("Enter Your OpenAI API Key 🗝️")
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", 
        value=st.session_state.get('openai_api_key', ''),
        help="Get your API key from https://openai.com/",
        type='password'
    )

    if openai_api_key == '':
        st.sidebar.warning("Please enter your OpenAI API key")
        st.stop()


    st.session_state['openai_api_key'] = openai_api_key

    openai_api_key = st.session_state['openai_api_key']
    os.environ["OPENAI_API_KEY"] = openai_api_key

    st.sidebar.title("Select your model")
    model_choice = st.sidebar.radio(
    "",
    model_options,
    index=0,)

    if model_choice == None or model_choice == '':
        st.sidebar.warning("Please select a model")
        st.stop()
    
    if 'workspace_bool' not in st.session_state.keys():
        st.session_state['workspace_bool'] = True
        if not os.path.exists('workspace'):
                os.mkdir(f'workspace')

    if 'log_bool' not in st.session_state.keys():
        st.session_state['log'] = True
        with open('workspace/terminal_log.log', 'w') as file:
            pass  # This will effectively erase the contents of the file

    logging.basicConfig(
        filename='workspace/terminal_log.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    folder_path = 'workspace/'

    # List all files in the folder
    file_list = os.listdir(folder_path)

    # list all the elements in the side bar
    st.sidebar.title("Workspace")
    st.sidebar.markdown(os.getcwd() + '/workspace')
    st.sidebar.write(file_list)

    logging.info(ui.WELCOME_MSG)

    print_bot('Programming task: ')

    ################################################# TASK ########################################################
    if 'task_message_bool' not in st.session_state.keys():
        if task_message := st.text_input('Programming task'):
            st.session_state.messages.append({"role": "user", "content": task_message})


        if task_message == '' or task_message == None:
            st.stop()

        st.session_state['task_message_bool'] = True
        st.session_state['task_message'] = task_message
    
    task_message = st.session_state['task_message']

    print_user(task_message)
    logging.info(f"Programming task: {task_message}")

    print_bot('Programming language: ')
    ################################################# END #########################################################
    if 'init_llm_bool' not in st.session_state.keys():
        st.session_state['init_llm_bool'] = True
        if model_choice == model_options[0]:
            st.session_state['llm'] = llm_init() 
        elif model_choice == model_options[1]:
            st.session_state['llm'] = llm_init(model_name="gpt-4",
                                               temperature=0.2,
                                               max_tokens=4000,
                                               model_kwargs={'frequency_penalty':0.2, 'presence_penalty':0})

    llm = st.session_state['llm']

    if 'comp_prompt_parser_bool' not in st.session_state.keys():
        st.session_state['comp_prompt_parser_bool'] = True
        st.session_state.comp_prompt, st.session_state.comp_parser = get_comp_prompt()
        st.session_state.comp_chain = LLMChain(
            llm=llm,
            prompt=st.session_state.comp_prompt,
            verbose=verbose
        )
    comp_chain = st.session_state['comp_chain']
    comp_prompt, comp_parser = st.session_state.comp_prompt, st.session_state.comp_parser
    ################################################# PROGRAMMING LANGUAGE ########################################################
    if 'lang_message_bool' not in st.session_state.keys():
        if lang_message := st.selectbox(label='Programming language',
                                        options=program_options,
                                        index=len(program_options)-1,
                                        placeholder='Select a programming language'):
            st.session_state.messages.append({"role": "user", "content": lang_message})
        
        if lang_message == '' or lang_message == None:
            st.stop()

        if lang_message == 'Other':
            lang_message = ''
            if lang_message := st.text_input('Programming language'):
                st.session_state.messages.append({"role": "user", "content": lang_message})
        
        if lang_message == '' or lang_message == None:
            st.stop()
            
        st.session_state['lang_message_bool'] = True
        st.session_state['lang_message'] = lang_message

    lang_message = st.session_state['lang_message']

    print_user(lang_message)
    logging.info(f"Programming language: {lang_message}")
    ################################################# END #########################################################

    ################################################# COMPONENTS ########################################################
    if 'comp_list_bool' not in st.session_state.keys():
        st.session_state['comp_list_bool'] = True
        comp_output = comp_chain.predict(input=task_message, lang=lang_message)
        st.session_state.comp_list = comp_parser.parse(comp_output).components

        
        st.session_state.comp_list_str = make_comp_list(st.session_state.comp_list)
    
    comp_list = st.session_state['comp_list']
    comp_list_str = st.session_state['comp_list_str']

    print_bot(ui.COMP_MSG_INIT)
    logging.info(ui.COMP_MSG_INIT)
    print_bot(comp_list_str)
    logging.info(comp_list_str)

    print_bot(ui.COMP_MSG_ADD)
    logging.info(ui.COMP_MSG_ADD)
    ################################################# END #########################################################

    ################################################# ADD MORE COMPONENTS ########################################################
    if 'add_comp_message_bool' not in st.session_state.keys():
        if add_comp_message := st.text_input("Components to be added: "):
            st.session_state.messages.append({"role": "user", "content": add_comp_message})
            logging.info(f"Components to be added: {add_comp_message}")

        if add_comp_message == '' or add_comp_message == None:
            st.stop()

        st.session_state['add_comp_message_bool'] = True
        st.session_state['add_comp_message_before'] = add_comp_message


    print_user(st.session_state['add_comp_message_before'])


    if st.session_state.add_comp_message_before.lower().__contains__('none'):
        st.session_state.add_comp_message = ""   
        add_comp_message = st.session_state['add_comp_message']
    else:
        add_comp_message = st.session_state['add_comp_message_before']
    

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
    ################################################# END #########################################################

    ################################################# REMOVE COMPONENTS ########################################################
    if 'rm_comp_message_bool' not in st.session_state.keys():
        if rm_comp_message := st.text_input("Components to be removed: "):
            logging.info(f"Components to be removed: {rm_comp_message}")

        if rm_comp_message == '' or rm_comp_message == None:
            st.stop()

        st.session_state['rm_comp_message_bool'] = True
        st.session_state['rm_comp_message_before'] = rm_comp_message

    print_user(st.session_state['rm_comp_message_before'])

    if st.session_state.rm_comp_message_before.lower().__contains__('none'):
        st.session_state.rm_comp_message = ""
        rm_comp_message = st.session_state['rm_comp_message']
    else:
        rm_comp_message = st.session_state['rm_comp_message_before']

    st.session_state.comp_list_rm = remove_comp_list(st.session_state.comp_list_add, rm_comp_message)
    st.session_state.comp_list_str_rm = make_comp_list(st.session_state.comp_list_rm)

    #rm_comp_message = st.session_state['rm_comp_message']
    comp_list = st.session_state['comp_list_rm']
    comp_list_str = st.session_state['comp_list_str_rm']
    ################################################# END #########################################################
    
    print_bot(ui.COMP_MSG_FINAL_1)
    logging.info(ui.COMP_MSG_FINAL_1)
    print_bot(comp_list_str)
    logging.info(comp_list_str)
    print_bot(ui.COMP_MSG_FINAL_2)
    logging.info(ui.COMP_MSG_FINAL_2)

##########################################################################################################
    if 'init_components_bool' not in st.session_state.keys():
        st.session_state.all_comps_1 = """"""
        st.session_state.all_comps_2_spec = """"""
        st.session_state.all_comps_2_func_list = """"""
        st.session_state.all_summary = ""

    # TODO: RESOLVE THIS ISSUE   
    all_comps_1 = st.session_state['all_comps_1']
    all_comps_2_spec = st.session_state['all_comps_2_spec']
    all_comps_2_func_list = st.session_state['all_comps_2_func_list']
    all_summary = st.session_state['all_summary']
    

    counter = 0

    for comp in comp_list.keys():

        # if not seen component before, generate new llm output, otherwise use previous output
        if comp not in st.session_state.keys():
            st.session_state['spec_prompt_'+comp], st.session_state.spec_end_str = get_qa_prompt(
                task=task_message, lang=lang_message,
                all_comps_1=all_comps_1, all_comps_2=all_comps_2_spec,
                curr_comp=comp, curr_comp_desc=comp_list[comp])
            st.session_state['spec_memory_'+comp] = ConversationBufferMemory()
            st.session_state['spec_chain_'+comp] = ConversationChain(
                llm=llm,
                prompt=st.session_state['spec_prompt_'+comp],
                memory=st.session_state['spec_memory_'+comp],
                verbose=verbose)
            
            init_human_input = "I want to implement '{comp}'".format(comp=comp)
            st.session_state['spec_output_'+comp] = st.session_state['spec_chain_'+comp].predict(input=init_human_input)
            st.session_state[comp] = True

        spec_prompt, spec_end_str = st.session_state['spec_prompt_'+comp], st.session_state["spec_end_str"]
        spec_memory, spec_chain = st.session_state['spec_memory_'+comp], st.session_state['spec_chain_'+comp]
        spec_output = st.session_state['spec_output_'+comp]

        print_bot(ui.SPEC_MSG_TITLE.format(comp=comp))
        logging.info(ui.SPEC_MSG_TITLE.format(comp=comp))
        print_bot(spec_output)
        logging.info(spec_output)

        if comp+'_complete' not in st.session_state.keys():
            st.session_state[comp+'_complete'] = False

        if comp+'_complete_early' not in st.session_state.keys():
            st.session_state[comp+'_complete_early'] = False

        if 'index_'+comp not in st.session_state.keys():
            st.session_state['index_'+comp] = 0
        
        output_counter = 0

        while spec_end_str not in spec_output:
                            if st.session_state[comp+'_complete_early'] and (output_counter+1 == st.session_state['index_'+comp]):
                                break

                            # This one is probably redundant because of >=
                            if st.session_state[comp+'_complete'] and (output_counter == st.session_state['index_'+comp]):
                                break

                            if comp+str(counter) not in st.session_state.keys():
                                if human_response := st.text_input(f"Answer: ", key=f"Answer {counter+1} for {comp}"):
                                    logging.info(f"Answer: {human_response}")

                                if human_response == '' or human_response == None:
                                    st.stop()
                                st.session_state[comp+str(counter)] = True
                                st.session_state[comp+str(counter)+'response'] = human_response

                            print_user(st.session_state[comp+str(counter)+'response']) # print user input

                            human_response = st.session_state[comp+str(counter)+'response']

                            if output_counter >= st.session_state['index_'+comp] and not st.session_state[comp+'_complete']:
                                st.session_state['index_'+comp] +=  1
                                spec_output = spec_chain.predict(input=human_response)
                                spec_output_clean = spec_output.replace(spec_end_str, "")
                                # add spec_output_clean to list of messages
                                if 'llm_msg_'+comp+"_"+str(output_counter) not in st.session_state.keys():
                                    st.session_state['llm_msg_'+comp+"_"+str(output_counter)] = spec_output_clean
                            else:
                                spec_output_clean = st.session_state['llm_msg_'+comp+"_"+str(output_counter)]
                            
                                

                            print_bot(spec_output_clean) # print LLM output to user
                            logging.info(spec_output_clean)
                            counter += 1
                            output_counter += 1 # used for session

        
        sum_prompt = get_summarize_prompt()

        if 'summary_chain_'+comp not in st.session_state.keys():
            st.session_state['summary_chain_'+comp] = LLMChain(
                llm=llm,
                prompt=sum_prompt,
                verbose=verbose
            )
        summary_chain = st.session_state['summary_chain_'+comp]

        spec_memory.return_messages = True


        if 'summary_'+comp not in st.session_state.keys():
            sum_output = summary_chain.predict(input=spec_memory.load_memory_variables({}))
            st.session_state.all_summary += sum_output

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
            
            st.session_state.all_comps_1, st.session_state.all_comps_2_spec, st.session_state.all_comps_2_func_list = make_func_list(comp, comp_list[comp],
                                                                                generate_func_list_output,
                                                                                all_comps_1,
                                                                                all_comps_2_spec,
                                                                                all_comps_2_func_list)
            st.session_state['summary_'+comp] = True
            
            st.session_state[comp+'_complete'] = True

            if output_counter < st.session_state['index_'+comp]:
                st.session_state[comp+'_complete_early'] = True
        else:
            print_bot(GEN_CODE_MSG.format(comp=comp))


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Currently implemented main generation for Python code
    if lang_message.lower().__contains__('python'):
        main_generator(task_message, lang_message, comp_list, st.session_state.all_summary, llm, verbose)

    print_bot(ui.FAREWELL_MSG)
    logging.info(ui.FAREWELL_MSG)
    logging.shutdown()


if __name__ == "__main__":
    main()

