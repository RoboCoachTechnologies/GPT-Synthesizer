import streamlit as st
import os
from ui import message_func
import gpt_synthesizer.ui as ui
from ui import message_func
import platform
import sysconfig
import sys

print(os.name)
print(platform.system())
print(sysconfig.get_platform())
print(sys.version, sys.platform)