import streamlit as st
import sys
import os
from datetime import datetime
from config import Config
from utils import Utils

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agents import run_research, test_search_tool
except ImportError as e:
    st.error(f"Error importing agents module: {e}")
    st.error("Please ensure all required dependencies are installed by running: pip install -r requirements.txt")
    st.stop()

# Page config
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #0066cc;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    .powered-by {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
        font-size: 1.1rem;
        color: #666;
    }
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .status-success {
        background-color: #28a745;
    }
    .status-warning {
        background-color: #ffc107;
        color: #212529;
    }
    .status-error {
        background-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "research_count" not in st.session_state:
    st.session_state.research_count = 0

def reset_chat():
    """Reset the chat history"""
    st.session_state.messages = []
    st.session_state.research_count = 0
    st.rerun()

def add_message(role: str, content: str):
    """Add a message to the chat history"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Sidebar
with st.sidebar:
    st.markdown("### 🔍 Research Configuration")
    
    # Status indicators
    st.markdown("### 🔧 System Status")
    
    # OpenAI status
    if Config.has_openai_key():
        st.markdown('<span class="status-badge status-success">✅ OpenAI Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-warning">⚠️ OpenAI Not Configured</span>', unsafe_allow_html=True)
    
    # Test search tool
    if st.button("🔍 Test Search Tool"):
        with st.spinner("Testing search functionality..."):
            try:
                result = test_search_tool()
                if result:
                    st.success("✅ Search tool working!")
                    with st.expander("Sample Results"):
                        st.text(Utils.truncate_text(result, 300))
                else:
                    st.error("❌ Search tool failed")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    # Statistics
    st.markdown("### 📊 Session Stats")
    st.metric("Queries Processed", st.session_state.research_count)
    st.metric("Messages", len(st.session_state.messages))
    
    # Configuration
    st.markdown("### ⚙️ Settings")
    show_timestamps = st.checkbox("Show timestamps", value=True)
    show_sources = st.checkbox("Show sources", value=True)
    
    # Clear chat
    st.markdown("---")
    if st.button("🗑️ Clear Chat", type="secondary"):
        reset_chat()
    
    # Help
    st.markdown("### 📚 Help")
    with st.expander("Usage Tips"):
        st.markdown("""
        **🎯 Effective Queries:**
        - Be specific and clear
        - Include context when needed
        - Ask follow-up questions
        
        **📝 Examples:**
        - "What is quantum computing?"
        - "Latest AI developments in 2024"
        - "How does blockchain work?"
        - "Climate change effects on agriculture"
        """)
    
    with st.expander("Configuration"):
        st.markdown("""
        **🔧 Setup:**
        1. Install dependencies: `pip install -r requirements.txt`
        2. (Optional) Add OpenAI key to `.env` file
        3. Run: `streamlit run app.py`
        
        **🤖 LLM Options:**
        - OpenAI GPT (requires API key)
        - Ollama (local, free)
        - Default fallback mode
        """)

# Main content
st.markdown(f'<h1 class="main-header">{Config.APP_TITLE}</h1>', unsafe_allow_html=True)

# Powered by section
st.markdown("""
<div class="powered-by">
    <span>Powered by</span>
    <strong>CrewAI</strong>
    <span>•</span>
    <strong>DuckDuckGo</strong>
    <span>•</span>
    <strong>Streamlit</strong>
</div>
""", unsafe_allow_html=True)

# Welcome message
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="chat-container">
        <h3>🎯 Welcome to Your AI Research Assistant!</h3>
        <p>I'm here to help you find comprehensive information on any topic. Just ask me a question and I'll:</p>
        <ul>
            <li>🔍 Search the web for current information</li>
            <li>📊 Analyze multiple sources</li>
            <li>📝 Create structured reports with citations</li>
            <li>🎯 Provide insights and key findings</li>
        </ul>
        <p><strong>Ready to start? Ask me anything!</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if show_timestamps:
            st.caption(f"🕐 {message.get('timestamp', '')}")
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a research question...", key="research_input"):
    # Validate input
    is_valid, validation_message = Utils.validate_query(prompt)
    if not is_valid:
        st.error(f"❌ {validation_message}")
    else:
        # Add user message
        add_message("user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            if show_timestamps:
                st.caption(f"🕐 {st.session_state.messages[-1]['timestamp']}")
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            if show_timestamps:
                st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
            
            # Progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Start research
                status_text.text("🔍 Searching the web...")
                progress_bar.progress(25)
                
                # Run research
                result = run_research(prompt)
                
                progress_bar.progress(75)
                status_text.text("📊 Analyzing results...")
                
                # Check result
                if result and not result.startswith("Research error:") and not result.startswith("Invalid query:"):
                    progress_bar.progress(100)
                    status_text.text("✅ Research complete!")
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display result
                    st.markdown(result)
                    
                    # Add to history
                    add_message("assistant", result)
                    
                    # Update count
                    st.session_state.research_count += 1
                    
                    # Success message
                    st.success("Research completed successfully!")
                    
                else:
                    # Handle errors
                    progress_bar.empty()
                    status_text.empty()
                    
                    error_msg = result if result else "An unknown error occurred."
                    st.error(f"❌ {error_msg}")
                    
                    # Add error to history
                    add_message("assistant", f"❌ {error_msg}")
                    
            except Exception as e:
                # Handle exceptions
                progress_bar.empty()
                status_text.empty()
                
                error_msg = f"An unexpected error occurred: {str(e)}"
                st.error(f"❌ {error_msg}")
                
                # Add error to history
                add_message("assistant", f"❌ {error_msg}")
                
                # Log error
                Utils.log_error(e, "Streamlit app")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 20px;'>
    <p>🤖 <strong>AI Research Assistant</strong> | Built with Streamlit, CrewAI, and DuckDuckGo</p>
    <p>For best results, ask specific questions and be patient while I research! 🔍</p>
    <p>💡 <strong>Tip:</strong> The more specific your question, the better the research results!</p>
</div>
""", unsafe_allow_html=True)