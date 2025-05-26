import streamlit as st
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.workflows.agentic_workflow import create_workflow
from config.settings import NVIDIA_API_KEY

st.title("🤖 Agentic Workflow")
st.write("Powered by Llama-3.3-Nemotron-Super-49B-V1")

# Check API key
if not NVIDIA_API_KEY:
    st.error("Please set your NVIDIA_API_KEY in the environment variables")
    st.stop()

# Initialize workflow
if "workflow" not in st.session_state:
    try:
        st.session_state.workflow = create_workflow()
        st.success("✅ Workflow initialized")
    except Exception as e:
        st.error(f"Failed to initialize workflow: {e}")
        st.stop()

# User input
query = st.text_area("Enter your query:", height=100, placeholder="e.g., What's the weather in San Francisco and calculate 15% tip on $67?")

if st.button("🚀 Execute Workflow") and query:
    # Initialize state
    initial_state = {
        "original_query": query,
        "tasks": [],
        "current_task_id": None,
        "iteration_count": 0,
        "final_answer": None,
        "should_continue": True,
        "feedback": []
    }
    
    # Execute workflow
    with st.spinner("🔄 Processing..."):
        try:
            result = st.session_state.workflow.invoke(initial_state)
            
            # Display results
            st.subheader("📋 Final Answer")
            st.write(result["final_answer"])
            
            # Show task breakdown
            st.subheader("🔍 Task Breakdown")
            for task in result["tasks"]:
                status_emoji = {"completed": "✅", "failed": "❌", "pending": "⏳"}.get(task.status, "❓")
                
                with st.expander(f"{status_emoji} Task {task.id}: {task.description}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Status:** {task.status}")
                        st.write(f"**Tool:** {task.tool_used}")
                    with col2:
                        if task.result:
                            st.write(f"**Result:** {task.result}")
                        if task.error:
                            st.error(f"**Error:** {task.error}")
            
            # Show iteration info
            st.info(f"Completed in {result['iteration_count']} iterations")
            
        except Exception as e:
            st.error(f"Workflow execution failed: {e}")

# Sidebar with info
st.sidebar.markdown("### 🔧 Configuration")
st.sidebar.markdown("### 📊 Available Tools")
st.sidebar.write("• 🌐 Web Search")
st.sidebar.write("• 🧮 Calculator") 
st.sidebar.write("• 🌤️ Weather")