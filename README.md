# Agentic-Workflow

An agentic workflow system powered by Llama-3.3-Nemotron-Super-49B-V1, built with LangGraph and LangChain.

## Overview

This project implements an agentic workflow system that orchestrates multiple AI agents to plan, execute tools, and reflect on their performance to solve complex tasks. The system provides a Streamlit-based UI for easy interaction.

### Features

- **Multi-agent orchestration**: Planning agent, Tool agent, and Reflection agent working together
- **Tool integration**: Calculator, Web Search, and Weather APIs
- **Interactive UI**: Easy-to-use Streamlit interface to input queries and see results
- **State management**: Robust workflow state tracking with LangGraph
- **LLM integration**: Powered by Llama-3.3-Nemotron-Super-49B-V1 via NVIDIA AI Foundation API

## Project Structure

```
Agentic-Workflow/
├── config/
│   └── settings.py                # Configuration settings
├── src/
│   ├── agents/
│   │   ├── plan_agent.py          # Task planning agent
│   │   ├── reflection_agent.py    # Task reflection agent
│   │   └── tool_agent.py          # Tool execution agent
│   ├── tools/
│   │   ├── calculator.py          # Calculator tool
│   │   ├── registry.py            # Tool registry
│   │   ├── weather.py             # Weather API tool
│   │   └── web_search.py          # Web search tool
│   ├── utils/
│   │   ├── nvidia_llm.py          # NVIDIA API integration
│   │   └── state.py               # State management
│   ├── workflows/
│   │   └── agentic_workflow.py    # Workflow definition
│   ├── app.py                     # Streamlit application
│   └── __init__.py
├── requirements.txt               # Project dependencies
├── run_app.py                     # Application runner
└── README.md                      # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- API keys:
  - NVIDIA AI Foundation API key (for LLM access)
  - Tavily API key (for web search)

### Environment Setup

#### Windows

1. Clone the repository:
```powershell
git clone https://github.com/yourusername/Agentic-Workflow.git
cd Agentic-Workflow
```

2. Create and activate a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory with your API keys:
```
NVIDIA_API_KEY=your_nvidia_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

#### Linux/macOS

1. Clone the repository:
```bash
git clone https://github.com/mherenow/Agentic-Workflow.git
cd Agentic-Workflow
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory with your API keys:
```
NVIDIA_API_KEY=your_nvidia_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## Running the Application

### Windows

```powershell
python run_app.py
```

### Linux/macOS

```bash
python3 run_app.py
```

The Streamlit app will start and be accessible in your web browser at `http://localhost:8501`.

## Usage

1. Enter your query in the text area. The system can handle complex multi-step tasks, such as:
   - "What's the weather in San Francisco and calculate 15% tip on $67?"
   - "Find the population of Tokyo and convert it to scientific notation"

2. Click "Execute Workflow" to start the agentic workflow.

3. The system will:
   - Break down your query into tasks
   - Execute appropriate tools for each task
   - Reflect on the results
   - Provide a comprehensive answer

4. The UI will show the final answer along with a breakdown of all tasks executed.

## Adding New Tools

To add a new tool to the system:

1. Create a new tool file in the `src/tools/` directory
2. Register the tool in `src/tools/registry.py`
3. Update the tool agent in `src/agents/tool_agent.py` to handle the new tool type

## Troubleshooting

- **API Key Issues**: Ensure your API keys are correctly set in the `.env` file
- **Dependency Problems**: If you encounter any dependency issues, try upgrading pip and reinstalling requirements:
  ```
  pip install --upgrade pip
  pip install -r requirements.txt
  ```
- **Streamlit Errors**: Make sure you're running the application from the project root directory

## License

[Specify your license here]

## Acknowledgments

- This project uses LangGraph and LangChain for agent orchestration
- Powered by NVIDIA's Llama-3.3-Nemotron-Super-49B-V1 model
- Tavily API for web search functionality