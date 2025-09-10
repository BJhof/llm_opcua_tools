This repository contains supporting material for the paper:

**Beyond Touch HMI: Control to your machines in natural language by utilizing LLMs and OPC-UA**

DOI: TBD

**Contents**
- tools_mcp.py: Contains the three tools (read,write,adjust) and the launch of the mcp-server with gradio
- tool_schema.json: Tool schema necessary to equip the two open-weight models GPT-oss:20b and Qwen3:32b
- load_tool_schema.py: Script to load the schema
- results: Input and output of the five tested models (GPT5, GPT5-mini, GPT5-nano, GPT-oss:20b, Qwen3:32b)
  - logged_restuls_{model}.xlsx
