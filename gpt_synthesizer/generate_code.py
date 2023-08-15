import os
import sys
import logging

# logging.basicConfig(
#     filename='../workspace/terminal_log.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # Define a custom stream handler to capture console output
# class ConsoleAndFileHandler(logging.StreamHandler):
#     def __init__(self, stream=None):
#         super().__init__(stream)
    
#     def emit(self, record):
#         super().emit(record)
#         self.stream.flush()  # Flush the stream to capture the output immediately

# # Create an instance of the custom handler
# console_handler = ConsoleAndFileHandler(sys.stdout)

# # Add the custom handler to the logger
# logger = logging.getLogger()
# logger.addHandler(console_handler)

from langchain.chains import LLMChain

from gpt_synthesizer.prompt import get_generate_code_prompt
from gpt_synthesizer.parser import get_code_from_chat
from gpt_synthesizer.ui import GEN_CODE_MSG


def code_generator(task, lang, curr_comp, curr_comp_desc, func_list, summary, llm, verbose=False):
    gen_code_prompt = get_generate_code_prompt()

    gen_code_chain = LLMChain(
        llm=llm,
        prompt=gen_code_prompt,
        verbose=verbose
    )

    gen_code_output = gen_code_chain.predict(task=task, lang=lang, curr_comp=curr_comp, curr_comp_desc=curr_comp_desc,
                                             func_list=func_list, summary=summary)

    chat_key = "all_output.txt"
    workspace = to_files(gen_code_output, chat_key)

    for filename in workspace.keys():
        if filename == chat_key:
            continue

        code = workspace[filename]

        if filename == 'README.md':
            filename = curr_comp + ' README.md'

        with open('../workspace/' + filename, 'w') as file:
            file.write(code)

    print(GEN_CODE_MSG.format(comp=curr_comp))
    logging.info(GEN_CODE_MSG.format(comp=curr_comp))


def to_files(chat, chat_key):
    workspace = dict()

    workspace[chat_key] = chat

    files = get_code_from_chat(chat)
    for file_name, code in files:
        workspace[file_name] = code

    return workspace
