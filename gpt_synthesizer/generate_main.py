import os
import logging

from langchain.chains import LLMChain

from gpt_synthesizer.prompt import get_generate_main_prompt
from gpt_synthesizer.ui import GEN_MAIN_MSG
from gpt_synthesizer.generate_code import to_files
from gpt_synthesizer.ui import print_bot

def main_generator(task, language, component_list, summary, llm, verbose=False):
    # Get the contents of the workspace
    folder_path = 'workspace/'

    # List all files in the folder
    file_list = os.listdir(folder_path)

    # Iterate through the files and read their contents
    total_contents = ''

    for filename in file_list:
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.py'):  # Ensure it's a file (not a subdirectory, etc.)
            with open(file_path, 'r') as file:
                file_contents = file.read()
                total_contents += f"### {filename}\n{file_contents}\n"

    gen_code_prompt = get_generate_main_prompt()

    gen_code_chain = LLMChain(
        llm=llm,
        prompt=gen_code_prompt,
        verbose=verbose
    )

    gen_code_output = gen_code_chain.predict(task=task, language=language, component_list=component_list,
                                             summary=summary, total_contents=total_contents)

    chat_key = "all_output.txt"
    to_files(gen_code_output, chat_key, 'main')

    print_bot(GEN_MAIN_MSG)
    logging.info(GEN_MAIN_MSG)
