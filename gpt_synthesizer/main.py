import logging
import os

from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory

from gpt_synthesizer.model import llm_init
from gpt_synthesizer.prompt import get_comp_prompt, get_qa_prompt, get_summarize_prompt, get_generate_func_list_prompt
from gpt_synthesizer.parser import make_comp_list, extend_comp_list, remove_comp_list, make_func_list
from gpt_synthesizer.generate_code import code_generator
from gpt_synthesizer.generate_main import main_generator
import gpt_synthesizer.ui as ui


def main(verbose = False):
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

    print(ui.WELCOME_MSG)
    logging.info(ui.WELCOME_MSG)

    task_message = input("Programming task: ")  # User-specified task
    logging.info(f"Programming task: {task_message}")

    lang_message = input("Programming language: ")  # User-specified language
    logging.info(f"Programming language: {lang_message}")

    comp_output = comp_chain.predict(input=task_message, lang=lang_message)
    comp_list = comp_parser.parse(comp_output).components

    comp_list_str = make_comp_list(comp_list)

    print(ui.COMP_MSG_INIT)
    logging.info(ui.COMP_MSG_INIT)

    print(comp_list_str)
    logging.info(comp_list_str)

    print(ui.COMP_MSG_ADD)
    logging.info(ui.COMP_MSG_ADD)

    add_comp_message = input("Components to be added: ")
    logging.info(f"Components to be added: {add_comp_message}")

    if add_comp_message.lower().__contains__('none'):
        add_comp_message = ""
        
    if len(add_comp_message) == 0:
        print(ui.COMP_MSG_UPDATE_NO_ADD)
        logging.info(ui.COMP_MSG_UPDATE_NO_ADD)
    else:
        comp_list = extend_comp_list(comp_list, add_comp_message)
        comp_list_str = make_comp_list(comp_list)
        print(ui.COMP_MSG_UPDATE_ADD)
        logging.info(ui.COMP_MSG_UPDATE_ADD)
        print(comp_list_str)
        logging.info(comp_list_str)

    print(ui.COMP_MSG_RM)
    logging.info(ui.COMP_MSG_RM)

    rm_comp_message = input("Components to be removed: ")
    logging.info(f"Components to be removed: {rm_comp_message}")
    comp_list = remove_comp_list(comp_list, rm_comp_message)
    comp_list_str = make_comp_list(comp_list)

    print(ui.COMP_MSG_FINAL_1)
    logging.info(ui.COMP_MSG_FINAL_1)
    print(comp_list_str)
    logging.info(comp_list_str)
    print(ui.COMP_MSG_FINAL_2)
    logging.info(ui.COMP_MSG_FINAL_2)

    all_comps_1 = """"""
    all_comps_2_spec = """"""
    all_comps_2_func_list = """"""

    all_summary = ""
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

        print(ui.SPEC_MSG_TITLE.format(comp=comp))
        logging.info(ui.SPEC_MSG_TITLE.format(comp=comp))
        print(spec_output)
        logging.info(spec_output)

        while spec_end_str not in spec_output:
            human_response = input("Answer: ")
            logging.info(f"Answer: {human_response}")
            spec_output = spec_chain.predict(input=human_response)
            spec_output_clean = spec_output.replace(spec_end_str, "")
            print(spec_output_clean)
            logging.info(spec_output_clean)

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

    print(ui.FAREWELL_MSG)
    logging.info(ui.FAREWELL_MSG)
    logging.shutdown()


if __name__ == "__main__":
    main()
