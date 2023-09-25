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
from ui import print_bot, print_user, GEN_CODE_MSG

program_options = ['','Python', 'C++', 'Java', 'Swift']

#print("\nI'm at a global level and what to see if I get called! I am above the main function!")

def main(verbose = False):
    #print('Setting up streamlit headers and first bot message')
    st.set_page_config(page_title="GPT Synthesizer", initial_sidebar_state='auto', menu_items=None)
    st.title("🚀🤖🧑‍💻GPT Synthesizer!!!")
    st.caption('Generate your code base on your task description and programming language!')
    print_bot("Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG)

    #print("I am making the initial message!")
    INITIAL_MESSAGE = [
        {"role": "user", "content": "Hi!"},
        {
            "role": "assistant",
            "content": "Hey there, I'm GPT Synthesizer, your code generation assistant, ready to realize your next dream project?!"+ui.WELCOME_MSG,
        },
    ]

    #print("creating session keys 'messages' and 'history' if they don't exist")
    if "messages" not in st.session_state.keys():
        #print("I am actually creating 'messages' ")
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
    # st.session_state.messages.append({"role": "assistant", "content": "here we go!"})


    #print("I am making the sidebar")
    st.sidebar.title("Enter Your OpenAI API Key 🗝️")
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", 
        value=st.session_state.get('openai_api_key', ''),
        help="Get your API key from https://openai.com/",
        type='password'
    )

    #print("I am checking the API key otherwise I am stopping and warning the user")
    if openai_api_key == '':
        st.sidebar.warning("Please enter your OpenAI API key")
        st.stop()

    # TODO: REMOVE THIS LINE BEFORE COMMITTING
    #print("I overwrote the API key with a hard coded one")

    #print("making key an environment variable and session state variable")
    st.session_state['openai_api_key'] = openai_api_key

    openai_api_key = st.session_state['openai_api_key']
    os.environ["OPENAI_API_KEY"] = openai_api_key

    if 'workspace_bool' not in st.session_state.keys():
        st.session_state['workspace_bool'] = True
        #print("setting up workspace folder")
        # Open the file in write mode
        if not os.path.exists('workspace'):
                os.mkdir(f'workspace')

    if 'log_bool' not in st.session_state.keys():
        st.session_state['log'] = True
        #print("setting up terminal log by erasing its contents if exists and setting up config")
        with open('workspace/terminal_log.log', 'w') as file:
            #print("I am erasing the terminal log file")
            pass  # This will effectively erase the contents of the file

    # TODO: CHECK IF THIS WELL PERSIST BETWEEN SESSIONS
    logging.basicConfig(
        filename='workspace/terminal_log.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if 'init_llm_bool' not in st.session_state.keys():
        st.session_state['init_llm_bool'] = True
        #print("instantiating LLM model")
        st.session_state['llm'] = llm_init()

    llm = st.session_state['llm']

    if 'comp_prompt_parser_bool' not in st.session_state.keys():
        st.session_state['comp_prompt_parser_bool'] = True
        #print("setting up the components prompt and parser")
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

    ################################################# TASK ########################################################
    if 'task_message_bool' not in st.session_state.keys():
        #print("I am asking user for their programming task")
        if task_message := st.text_input('Programming task'):
            st.session_state.messages.append({"role": "user", "content": task_message})

        #print('checking if task message is empty')

        if task_message == '' or task_message == None:
            #st.warning("Please enter your programming task")
            st.stop()

        st.session_state['task_message_bool'] = True
        st.session_state['task_message'] = task_message
    
    task_message = st.session_state['task_message']

    #print('displaying user programming task')
    print_user(task_message)
    logging.info(f"Programming task: {task_message}")

    print_bot('Programming language: ')
    ################################################# END #########################################################

    ################################################# PROGRAMMING LANGUAGE ########################################################
    if 'lang_message_bool' not in st.session_state.keys():
        #print("I am asking user for their programming language")
        if lang_message := st.selectbox(label='Programming language',
                                        options=program_options,
                                        index=0,
                                        placeholder='Select a programming language'):
            st.session_state.messages.append({"role": "user", "content": lang_message})
        
        #print('checking if lang message is empty')
        if lang_message == '' or lang_message == None:
            #st.warning("Please enter your programming task")
            st.stop()
        
        st.session_state['lang_message_bool'] = True
        st.session_state['lang_message'] = lang_message

    lang_message = st.session_state['lang_message']
    #print(f"current lang_message is {lang_message} and current task_message is {task_message}")

    #print("displaying user's programming language")
    print_user(lang_message)
    logging.info(f"Programming language: {lang_message}")
    ################################################# END #########################################################

    ################################################# COMPONENTS ########################################################
    if 'comp_list_bool' not in st.session_state.keys():
        st.session_state['comp_list_bool'] = True
        #print('predicting component output and parsing it to get a list of components')
        comp_output = comp_chain.predict(input=task_message, lang=lang_message)
        st.session_state.comp_list = comp_parser.parse(comp_output).components

        
        #print("making component list and displaying it")
        st.session_state.comp_list_str = make_comp_list(st.session_state.comp_list)
    
    comp_list = st.session_state['comp_list']
    comp_list_str = st.session_state['comp_list_str']

    print_bot(ui.COMP_MSG_INIT)
    logging.info(ui.COMP_MSG_INIT)
    print_bot(comp_list_str)
    logging.info(comp_list_str)

    #print("I am asking user if they want to add or remove components")
    print_bot(ui.COMP_MSG_ADD)
    logging.info(ui.COMP_MSG_ADD)
    ################################################# END #########################################################

    ################################################# ADD MORE COMPONENTS ########################################################
    if 'add_comp_message_bool' not in st.session_state.keys():
        #print("text input for components to be added")
        if add_comp_message := st.text_input("Components to be added: "):
            st.session_state.messages.append({"role": "user", "content": add_comp_message})
            logging.info(f"Components to be added: {add_comp_message}")

        #print('checking if add comp message is empty')
        if add_comp_message == '' or add_comp_message == None:
            #st.warning("Please enter your programming task")
            st.stop()

        st.session_state['add_comp_message_bool'] = True
        st.session_state['add_comp_message'] = add_comp_message


    #print('checking if add comp message contains none')
    if st.session_state.add_comp_message.lower().__contains__('none'):
        st.session_state.add_comp_message = ""   
    
    add_comp_message = st.session_state['add_comp_message']


    #print('extending component list with components to be added unless is none')
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
        #print("I am asking user if they want to remove components")
        #print("text input for components to be removed")
        if rm_comp_message := st.text_input("Components to be removed: "):
            logging.info(f"Components to be removed: {rm_comp_message}")

        #print('checking if rm comp message is empty')
        if rm_comp_message == '' or rm_comp_message == None:
            #st.warning("Please enter your programming task")
            st.stop()

        st.session_state['rm_comp_message_bool'] = True
        st.session_state['rm_comp_message'] = rm_comp_message

        #print('checking if rm comp message contains none')
        if rm_comp_message.lower().__contains__('none'):
            rm_comp_message = ""
            st.session_state['rm_comp_message'] = rm_comp_message

        #print('removing components from component list unless is none (no logic for utilizing none)')
        st.session_state.comp_list_rm = remove_comp_list(st.session_state.comp_list_add, rm_comp_message)
        st.session_state.comp_list_str_rm = make_comp_list(st.session_state.comp_list_rm)

    rm_comp_message = st.session_state['rm_comp_message']
    comp_list = st.session_state['comp_list_rm']
    comp_list_str = st.session_state['comp_list_str_rm']
    ################################################# END #########################################################
    
    #print("displaying final component list")
    print_bot(ui.COMP_MSG_FINAL_1)
    logging.info(ui.COMP_MSG_FINAL_1)
    print_bot(comp_list_str)
    logging.info(comp_list_str)
    print_bot(ui.COMP_MSG_FINAL_2)
    logging.info(ui.COMP_MSG_FINAL_2)

##########################################################################################################
    #print('setting components and all summary to empty strings')
    if 'init_components_bool' not in st.session_state.keys():
        st.session_state.all_comps_1 = """"""
        st.session_state.all_comps_2_spec = """"""
        st.session_state.all_comps_2_func_list = """"""
        st.session_state.all_summary = ""

    # TODO: RESOLVE THIS ISSUE  
    # FIXED: 
    all_comps_1 = st.session_state['all_comps_1']
    all_comps_2_spec = st.session_state['all_comps_2_spec']
    all_comps_2_func_list = st.session_state['all_comps_2_func_list']
    all_summary = st.session_state['all_summary']
    

    counter = 0
    #print("I'm about to enter the for loop and counter is equal to ", counter)





    # FIXME: create session state that indicates if component has been completed, then 'continue' to next component

    for comp in comp_list.keys():
        # print("I'm in the for loop and counter is equal to ", counter)
        # print('current component is ', comp)
        # print("getting spec prompt and end string")
        # print('initializing human input to implement component')

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

        #print("printing bot and logging spec message title and spec output")
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

        # print('\nthis is the index_comp', st.session_state['index_'+comp])
        # print('this is the output_counter', output_counter)
        # print('the comp is ', comp)
        # print('the comp_complete is ', st.session_state[comp+'_complete'])
        # print('the comp_complete_early is ', st.session_state[comp+'_complete_early'])
        while spec_end_str not in spec_output:
                            if st.session_state[comp+'_complete_early'] and (output_counter+1 == st.session_state['index_'+comp]):
                                break

                            # This one is probably redundant because of >=
                            if st.session_state[comp+'_complete'] and (output_counter == st.session_state['index_'+comp]):
                                break

                            if human_response := st.text_input(f"Answer {counter+1}: ", key=f"Answer {counter+1} for {comp}"):
                                logging.info(f"Answer: {human_response}")

                            #print('checking if human response is empty')
                            if human_response == '' or human_response == None:
                                #st.warning("Please enter your programming task")
                                #print('\tresponse empty -- stopping streamlit loop')
                                st.stop()
                            #else: # TODO: [self debug] REMOVE THIS ELSE STATEMENT
                                #print('\tresponse received -- continuing streamlit loop\n\t\tresponse is: ', human_response)
                            


                            if output_counter >= st.session_state['index_'+comp] and not st.session_state[comp+'_complete']:
                                #print("\tPrinting LLM -=- output_counter: ", output_counter, " index: ", st.session_state['index_'+comp])
                                st.session_state['index_'+comp] +=  1
                                spec_output = spec_chain.predict(input=human_response)
                                spec_output_clean = spec_output.replace(spec_end_str, "")
                                # add spec_output_clean to list of messages
                                if 'llm_msg_'+comp+"_"+str(output_counter) not in st.session_state.keys():
                                    st.session_state['llm_msg_'+comp+"_"+str(output_counter)] = spec_output_clean
                                    #print("\tAdding " + 'llm_msg_'+comp+"_"+str(output_counter))
                            else:
                                #print("\tNot Reprinting LLM -=- output_counter: ", output_counter, " index: ", st.session_state['index_'+comp])
                                spec_output_clean = st.session_state['llm_msg_'+comp+"_"+str(output_counter)]
                            
                                

                            print_bot(spec_output_clean) # print LLM output to user
                            logging.info(spec_output_clean)
                            #print('incrementing counter')
                            counter += 1
                            #print('incrementing output counter')
                            output_counter += 1 # used for session

        
        
        
        #print('I am immediately after the while loop and counter is equal to ', counter)
        #print("getting summary prompt")
        sum_prompt = get_summarize_prompt()

        if 'summary_chain_'+comp not in st.session_state.keys():
            st.session_state['summary_chain_'+comp] = LLMChain(
                llm=llm,
                prompt=sum_prompt,
                verbose=verbose
            )
        summary_chain = st.session_state['summary_chain_'+comp]

        #print('accumulating all summary')
        spec_memory.return_messages = True


        if 'summary_'+comp not in st.session_state.keys():
            sum_output = summary_chain.predict(input=spec_memory.load_memory_variables({}))
            st.session_state.all_summary += sum_output

            #print('getting generate func list prompt')
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

            #print('generating code')
            code_generator(task_message, lang_message, comp, comp_list[comp],
                        generate_func_list_output, sum_output, llm, verbose)
            
            #print('making function list')
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
    #print('generating main function and just left for loop')
    if lang_message.lower().__contains__('python'):
        main_generator(task_message, lang_message, comp_list, st.session_state.all_summary, llm, verbose)

    #print('printing farewell message and shutting down logging')
    print_bot(ui.FAREWELL_MSG)
    logging.info(ui.FAREWELL_MSG)
    logging.shutdown()


if __name__ == "__main__":
    #print("I am right before the main function is called!")
    main()
    #print("I am right after the main function is called!")

