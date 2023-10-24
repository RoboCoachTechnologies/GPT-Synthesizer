# GPT Synthesizer

**Collaboratively implement an entire software project with the help of an AI.**

GPT-Synthesizer walks you through the problem statement and explores the design space with you through a carefully moderated interview process. If you have no idea where to start and how to describe your software project, GPT Synthesizer can be your best friend.

## What makes GPT Synthesizer unique?

The design philosophy of GPT Synthesizer is rooted in the core, and rather contrarian, belief that a single prompt is not enough to build a complete codebase for complex software. This is mainly due to the fact that, even in the presence of powerful LLMs, there are still many crucial details in the design specification that cannot be effectively captured in a single prompt. Attempting to include every bit of detail in a single prompt, if not impossible, would cause a loss of efficiency of the LLM engine. Powered by [LangChain](https://python.langchain.com/docs/get_started/introduction), GPT Synthesizer captures the design specification, step by step, through an AI-directed dialogue that explores the design space with the user.

GPT Synthesizer interprets the initial prompt as a high-level description of a programming task. Then, through a process, which we named “prompt synthesis”, GPT Synthesizer compiles the initial prompt into multiple program components that the user might need for implementation. This step essentially turns 'unknown unknowns' into 'known unknowns', which can be very helpful for novice programmers who want to understand the overall flow of their desired implementation. Next, GPT Synthesizer and the user collaboratively find out the design details that will be used in the implementation of each program component.

Different users might prefer different levels of interactivity depending on their unique skill set, their level of expertise, as well as the complexity of the task at hand. GPT Synthesizer distinguishes itself from other LLM-based code generation tools by finding the right balance between user participation and AI autonomy.

## Installation

- `pip install gpt-synthesizer`

- For development:
  - `git clone https://github.com/RoboCoachTechnologies/GPT-Synthesizer.git`
  - `cd GPT-Synthesizer`
  - `pip install -e .`

## Usage

GPT Synthesizer is easy to use. It provides you with an intuitive AI assistant in your command-line interface. It also provides an intuitive user interface using Streamlit. Watch these demos to see how GPT Synthesizer works:
- [GPT-Synthesizer Release v0.0.2 demo: a snake game](https://www.youtube.com/watch?v=zFJDQOtIFGA)
- [GPT-Synthesizer Release v0.0.3 demo: a tic-tac-toe game](https://www.youtube.com/watch?v=_JdmzpXLyE0)
- [GPT-Synthesizer short demo: how to install](https://www.youtube.com/watch?v=D_kdzOUTe0E)
- [GPT-Synthesizer short demo: how to add/remove components](https://www.youtube.com/watch?v=mOHWS83HfOU)

GPT Synthesizer uses OpenAI's `gpt-3.5-turbo-16k` as the default LLM.

**Streamlit App**:

- Start GPT Synthesizer by typing `gpt-synthesizer-streamlit` in the terminal.
- Input your OpenAI API key in the sidebar
- Select the model you wish to use in the sidebar

**Command Line Interface**:

- Setup your OpenAI API key: `export OPENAI_API_KEY=[your api key]`
- Start GPT Synthesizer by typing `gpt-synthesizer` in the terminal.

**How it works**:

- Briefly describe your programming task and the implementation language:
  - `Programming task: *I want to implement an edge detection method from a live camera feed.*`
  - `Programming language: *python*`
- GPT Synthesizer will analyze your task and suggest a set of components needed for the implementation.
  - You can add more components by listing them in quotation marks: `Components to be added: *Add 'component 1: what component 1 does', 'component 2: what component 2 does', and 'component 3: what component 3 does' to the list of components.*`
  - You can remove any redundant component in a similar manner: `Components to be removed: *Remove 'component 1' and 'component 2' from the list of components.*`
- After you are done with modifying the component list, GPT Synthesizer will start asking questions in order to find all the details needed for implementing each component.
- When GPT Synthesizer learns about your specific requirements for each component, it will write the code for you!
- You can find the implementation in the `workspace` directory. For transparency, the UI will put the path and the content of the `workspace` in the sidebar.


## Make your own GPT Synthesizer!

GPT Synthesizer’s code is easy to read and understand. Anyone can customize the code for a specific application. The codebase is tightly integrated with [LangChain](https://python.langchain.com/docs/get_started/introduction), allowing utilization of various tools such as [internet search](https://python.langchain.com/docs/integrations/tools/ddg) and [vector databases](https://python.langchain.com/docs/modules/memory/types/vectorstore_retriever_memory).

GPT Synthesizer's hierarchical strategy to build the codebase allows OpenAI’s GPT3.5 to be a viable option for the backend LLM. We believe GPT3.5 provides a good trade-off between cost and contextual understanding, while GPT4 might be too expensive for many use cases. Nevertheless, [switching to another LLM](https://python.langchain.com/docs/integrations/llms/) is made easy thanks to LangChain integration.

## Roadmap

GPT Synthesizer will be actively maintained as an open-source project. We welcome everyone to contribute to our community of building systems for human-in-the-loop code generation!

Here is a (non-exhaustive) list of our future plans for GPT Synthesizer:

- An additional step in code generation that ensures creating a main/entrypoint. This feature has already been implemented for the Python language.
- Creating setup instructions based on the programming language, e.g. `CMakelists.txt` for C++ and `setup.py`+`requirements.txt` for Python.
- Adding benchmarks and testing scripts.

## Contact

For business inquiries, such as consulting or contracting jobs, please contact robocoachtechnologies@gmail.com. 

