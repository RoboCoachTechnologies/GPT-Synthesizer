from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
import os
from prompt import get_generate_main_prompt
from gpt_synthesizer.parser import get_code_from_chat
import logging
from ui import GEN_MAIN_MSG


def to_files(chat, chat_key):
    workspace = dict()

    workspace[chat_key] = chat

    files = get_code_from_chat(chat)
    for file_name, code in files:
        workspace[file_name] = code

    return workspace


def main_generator(task, language, component_list, summary, llm, verbose=False):
    # Get the contents of the workspace
    folder_path = '../workspace/'

    # List all files in the folder
    file_list = os.listdir(folder_path)

    # Iterate through the files and read their contents
    total_contents = ''

    for filename in file_list:
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.py'):  # Ensure it's a file (not a subdirectory, etc.)
            print(f"Implementation of {filename}")
            with open(file_path, 'r') as file:
                file_contents = file.read()
                #print(f"Contents of {filename}:\n{file_contents}\n")
                total_contents += f"### {filename}\n{file_contents}\n"
    # print(f"Total contents:\n{total_contents}")

    gen_code_prompt = get_generate_main_prompt()

    gen_code_chain = LLMChain(
        llm=llm,
        prompt=gen_code_prompt,
        verbose=verbose
    )

    gen_code_output = gen_code_chain.predict(task=task, language=language, component_list=component_list,
                                             summary=summary, total_contents=total_contents)

    chat_key = "all_output.txt"
    workspace = to_files(gen_code_output, chat_key)

    for filename in workspace.keys():
        if filename == chat_key:
            continue

        code = workspace[filename]

        if filename == 'README.md':
            filename = 'main' + ' README.md'

        with open('../workspace/' + filename, 'w') as file:
            file.write(code)

    print(GEN_MAIN_MSG)
    logging.info(GEN_MAIN_MSG)
    
# if __name__ == '__main__':

#     from model import llm_init


#     model_config = "/../config/model_params.yaml"
#     verbose = True


#     llm = llm_init(model_config)
#     task_message = ''
#     lang_message = 'Python'
#     output = '''
#             - Human wants to implement a 'Game board'
#             - AI asks for more details about the 'Game board'
#             - Human wants the 'Game board' to display the current state of a tik-tak-toe game in the terminal
#             - AI asks for specific format or design for the 'Game board'
#             - Human says any format is fine
#             - AI asks for size or dimensions of the 'Game board'
#             - Human specifies it should be a 3x3 grid
#             - AI asks if cells should be labeled or numbered
#             - Human wants cells labeled with numbers from 1 to 9
#             - AI asks if 'Game board' should have initial state or start empty
#             - Human wants it to start empty
#             - AI confirms all details and will proceed with designing the 'Game board'
#             '''
#     comp = 'Game board'
#     comp_list = {
#   "components": [
#     "Game board",
#     "Player",
#     "AI player",
#     "Game logic"
#   ]
# }
#     main_generator(task_message, lang_message, comp_list, comp, output, llm)