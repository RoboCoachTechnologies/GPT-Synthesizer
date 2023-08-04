import re

from typing import List, Dict

from pydantic import BaseModel, Field

from langchain.output_parsers import PydanticOutputParser


# Data structure for the output of COMP
class CompList(BaseModel):
    components: Dict[str, str] = Field(description="dictionary containing component names as keys and component descriptions as values")


def get_comp_parser():
    return PydanticOutputParser(pydantic_object=CompList)


def make_comp_list(comp_list):
    comp_list_str = ""
    for comp in comp_list.keys():
        comp_list_str += "- " + comp + ": " + comp_list[comp] + "\n"
    return comp_list_str


def extend_comp_list(comp_list, add_msg):
    add_list = re.findall(r"'(.*?)'", add_msg, re.DOTALL)
    for new_comp in add_list:
        comp_split = new_comp.split(":")
        comp_list[comp_split[0]] = comp_split[1]
    return comp_list


def remove_comp_list(comp_list, rm_msg):
    rm_list = re.findall(r"'(.*?)'", rm_msg, re.DOTALL)
    for rm_comp in rm_list:
        del comp_list[rm_comp]
    return comp_list


# Data structure for the output of STARTER
class StarterQA(BaseModel):
    question: str = Field(description="question asked by AI")
    more_q: str = Field(description="whether or not the AI needs to ask more questions")


def get_starter_parser():
    return PydanticOutputParser(pydantic_object=StarterQA)


class FuncDesc(BaseModel):
    name: str = Field(description="name of the function")
    description: str = Field(description="high-level description of the functionality")
    inputs: List[str] = Field(description="list of inputs of the function")
    outputs: List[str] = Field(description="list of outputs of the function")


def get_func_desc_parser():
    return PydanticOutputParser(pydantic_object=FuncDesc)


# Data structure for the output of the initial code generation
class FuncList(BaseModel):
    function_list: List[FuncDesc] = Field(description="list of functions to be implemented")


def get_func_list_parser():
    return PydanticOutputParser(pydantic_object=FuncList)


def get_code_from_chat(chat):
    # Get all code blocks and preceding file names
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters
        path = re.sub(r'[<>"|?*]', "", match.group(1))

        # Remove leading and trailing brackets
        path = re.sub(r"^\[(.*)\]$", r"\1", path)

        # Remove leading and trailing backticks
        path = re.sub(r"^`(.*)`$", r"\1", path)

        # Remove trailing ]
        path = re.sub(r"\]$", "", path)

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    readme = chat.split("```")[0] + '\n' + chat.split("```")[-1]
    files.append(("README.md", readme))

    # Return the files
    return files


def make_func_list(comp_name, comp_desc, comp_func_list, all_comps_1, all_comps_2_spec, all_comps_2_func_list):
    if len(all_comps_1) == 0:
        all_comps_1 = """The list below shows the components with their corresponding description and functions that have been implemented so far:"""
        all_comps_2_spec = """The other components in the list above are just provided for context so you know what has been already implemented."""
        all_comps_2_func_list = """The other components in the list above are just provided for context so you know what has been already implemented.
        However, when you generate your list of functions for implementing '{curr_comp}', you should make sure that you are not duplicating any of the functions above since they have been already implemented."""

    all_comps_1 = all_comps_1 + "\n---\n" + comp_name + ": " + comp_desc + ".\n" + comp_func_list + "\n---\n"
    return all_comps_1, all_comps_2_spec, all_comps_2_func_list
