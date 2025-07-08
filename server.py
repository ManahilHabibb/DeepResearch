import asyncio
import sys
import os
from typing import Optional
from config import Config
from utils import Utils

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agents import run_research, test_search_tool
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Try to import MCP components
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    print("MCP not available. Install with: pip install mcp fastmcp")
    MCP_AVAILABLE = False

if MCP_AVAILABLE:
    # Initialize MCP server
    mcp = FastMCP("ai_research_assistant")
    
    @mcp.tool()
    async def crew_research(query: str) -> str:
        """
        Perform comprehensive research on a given query using AI agents.
        
        Args:
            query: The research question or topic to investigate
            
        Returns:
            str: Comprehensive research report with citations
        """
        try:
            # Validate query
            is_valid, message = Utils.validate_query(query)
            if not is_valid:
                return f"Error: {message}"
            
            Utils.log_info(f"MCP Research request: {query}")
            
            # Run research in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_research, query)
            
            return result
            
        except Exception as e:
            Utils.log_error(e, "crew_research")
            return f"Research error: {str(e)}"
    
    @mcp.tool()
    async def health_check() -> str:
        """
        Check if the research system is working properly.
        
        Returns:
            str: Health status message
        """
        try:
            Utils.log_info("MCP Health check requested")
            
            # Test search functionality
            loop = asyncio.get_event_loop()
            test_result = await loop.run_in_executor(None, test_search_tool)
            
            if test_result:
                status = "✅ Research system is healthy and ready!"
                if Config.has_openai_key():
                    status += " (OpenAI configured)"
                else:
                    status += " (Using fallback mode)"
                return status
            else:
                return "⚠️ Research system has issues with search functionality"
                
        except Exception as e:
            Utils.log_error(e, "health_check")
            return f"❌ Health check failed: {str(e)}"
    
    @mcp.tool()
    async def get_capabilities() -> str:
        """
        Get information about the research system's capabilities.
        
        Returns:
            str: Description of available capabilities
        """
        capabilities = f"""
🔍 **AI Research Assistant Capabilities**

**🌐 Web Search:**
- DuckDuckGo integration for web searches
- Up to {Config.MAX_SEARCH_RESULTS} results per query
- Real-time information retrieval
- Timeout protection ({Config.SEARCH_TIMEOUT}s)

**🤖 AI Agents:**
- **Web Searcher:** Finds relevant information online
- **Research Analyst:** Analyzes and extracts insights
- **Technical Writer:** Creates structured reports

**📊 Output Features:**
- Comprehensive markdown reports
- Proper source citations
- Structured analysis with key insights
- Executive summaries

**⚙️ Configuration:**
- OpenAI GPT support: {"✅ Configured" if Config.has_openai_key() else "❌ Not configured"}
- Ollama support: ✅ Available
- Fallback mode: ✅ Always available
- Async processing: ✅ Supported

**💡 Example queries:**
- "What is quantum computing and its applications?"
- "Latest developments in artificial intelligence 2024"
- "Climate change impact on global agriculture"
- "Cryptocurrency market trends and analysis"
- "Sustainable energy solutions comparison"

**🔧 System Status:**
- Search functionality: {"✅ Working" if test_search_tool() else "❌ Issues detected"}
- Configuration: {"✅ Full features" if Config.has_openai_key() else "⚠️ Basic mode"}
"""
        return capabilities
    
    @mcp.tool()
    async def quick_search(query: str) -> str:
        """
        Perform a quick web search without full analysis.
        
        Args:
            query: The search query
            
        Returns:
            str: Raw search results
        """
        try:
            # Validate query
            is_valid, message = Utils.validate_query(query)
            if not is_valid:
                return f"Error: {message}"
            
            Utils.log_info(f"MCP Quick search: {query}")
            
            from agents import simple_research
            
            # Run simple search
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, simple_research, query)
            
            return result
            
        except Exception as e:
            Utils.log_error(e, "quick_search")
            return f"Search error: {str(e)}"

def run_mcp_server():
    """Run the MCP server"""
    try:
        print("🚀 Starting MCP Research Server...")
        print("Available tools:")
        print("  • crew_research: Comprehensive research with AI agents")
        print("  • quick_search: Fast web search without analysis")
        print("  • health_check: System health verification")
        print("  • get_capabilities: System capabilities overview")
        print("📡 Server ready for connections...")
        
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down MCP server...")
    except Exception as e:
        Utils.log_error(e, "MCP server")
        print(f"❌ Server error: {e}")
        sys.exit(1)

def run_standalone_mode():
    """Run in standalone mode for testing"""
    print("🔍 AI Research Assistant - Standalone Mode")
    print("=" * 50)
    
    # Test system
    print("Testing system...")
    test_result = test_search_tool()
    if test_result:
        print("✅ Search system working")
    else:
        print("❌ Search system issues")
    
    # Interactive mode
    print("\nEntering interactive mode. Type 'quit' to exit.")
    
    while True:
        try:
            query = input("\n🔍 Research Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print(f"\n🔄 Researching: {query}")
            print("=" * 50)
            
            result = run_research(query)
            print(result)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--standalone":
        run_standalone_mode()
    elif MCP_AVAILABLE:
        run_mcp_server()
    else:
        print("MCP not available. Running in standalone mode.")
        run_standalone_mode()