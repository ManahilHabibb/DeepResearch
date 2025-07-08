import os
from typing import Type, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from duckduckgo_search import DDGS
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from config import Config
from utils import Utils
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DuckDuckGoSearchInput(BaseModel):
    query: str = Field(description="The search query to perform")

class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Web Search"
    description: str = "Search the web for information using DuckDuckGo"
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput
    
    def _run(self, query: str) -> str:
        try:
            Utils.log_info(f"Searching for: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=Config.MAX_SEARCH_RESULTS))
                
                if not results:
                    return "No search results found."
                
                return Utils.format_search_results(results)
                
        except Exception as e:
            Utils.log_error(e, "DuckDuckGo search")
            return f"Search error: {str(e)}"

def simple_research(query: str) -> str:
    """Simple research function that just searches and formats results"""
    try:
        # Validate query
        is_valid, message = Utils.validate_query(query)
        if not is_valid:
            return f"Invalid query: {message}"
        
        Utils.log_info(f"Starting simple research for: {query}")
        
        # Use the search tool directly
        search_tool = DuckDuckGoSearchTool()
        search_results = search_tool._run(query)
        
        if search_results.startswith("Search error:"):
            return search_results
        
        # Create research report
        report = Utils.create_research_report(query, search_results)
        
        return report
        
    except Exception as e:
        Utils.log_error(e, "simple_research")
        return f"Research error: {str(e)}"

def create_crew_with_llm(query: str) -> Optional[Crew]:
    """Create crew with LLM configuration"""
    try:
        from langchain_openai import ChatOpenAI
        
        search_tool = DuckDuckGoSearchTool()
        
        # Configure LLM
        llm_config = Config.get_llm_config()
        
        if llm_config["provider"] == "openai":
            llm = ChatOpenAI(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=0.1
            )
        else:
            # Fallback to default or Ollama
            llm = None  # Let CrewAI use default
        
        # Create agents
        web_searcher = Agent(
            role="Web Research Specialist",
            goal="Find comprehensive and relevant information from web sources",
            backstory="You are an expert web researcher with skills in finding accurate, up-to-date information from reliable sources.",
            verbose=Config.CREWAI_VERBOSE,
            allow_delegation=True,
            tools=[search_tool],
            llm=llm
        )
        
        research_analyst = Agent(
            role="Research Analyst",
            goal="Analyze search results and extract key insights and patterns",
            backstory="You are a skilled analyst who can identify important information, trends, and insights from multiple sources.",
            verbose=Config.CREWAI_VERBOSE,
            allow_delegation=True,
            llm=llm
        )
        
        technical_writer = Agent(
            role="Technical Writer",
            goal="Create well-structured, comprehensive research reports",
            backstory="You are an expert technical writer who creates clear, organized, and informative reports with proper citations.",
            verbose=Config.CREWAI_VERBOSE,
            allow_delegation=False,
            llm=llm
        )
        
        # Create tasks
        search_task = Task(
            description=f"Search for comprehensive information about: {query}. Focus on finding current, accurate, and relevant sources.",
            agent=web_searcher,
            expected_output="Detailed search results with multiple sources and relevant information.",
            tools=[search_tool]
        )
        
        analysis_task = Task(
            description="Analyze the search results and identify key points, trends, and important insights.",
            agent=research_analyst,
            expected_output="Structured analysis highlighting key findings and insights.",
            context=[search_task]
        )
        
        writing_task = Task(
            description="Create a comprehensive research report based on the analysis, including proper structure and citations.",
            agent=technical_writer,
            expected_output="A well-formatted research report with clear sections, key findings, and proper citations.",
            context=[analysis_task]
        )
        
        return Crew(
            agents=[web_searcher, research_analyst, technical_writer],
            tasks=[search_task, analysis_task, writing_task],
            verbose=Config.CREWAI_VERBOSE,
            process=Process.sequential
        )
        
    except Exception as e:
        Utils.log_error(e, "create_crew_with_llm")
        return None

def run_research(query: str) -> str:
    """Main research function with multiple fallback strategies"""
    try:
        # Validate query
        is_valid, message = Utils.validate_query(query)
        if not is_valid:
            return f"Invalid query: {message}"
        
        Utils.log_info(f"Starting research for: {query}")
        
        # Strategy 1: Try CrewAI with LLM
        if Config.has_openai_key():
            try:
                crew = create_crew_with_llm(query)
                if crew:
                    Utils.log_info("Using CrewAI with LLM")
                    result = crew.kickoff()
                    
                    # Handle different result types
                    if hasattr(result, 'raw'):
                        return result.raw
                    elif hasattr(result, 'result'):
                        return result.result
                    else:
                        return str(result)
                        
            except Exception as e:
                Utils.log_error(e, "CrewAI with LLM")
        
        # Strategy 2: Try CrewAI without LLM configuration
        try:
            Utils.log_info("Trying CrewAI with default configuration")
            crew = create_crew_with_llm(query)  # Will use default LLM
            if crew:
                result = crew.kickoff()
                
                if hasattr(result, 'raw'):
                    return result.raw
                elif hasattr(result, 'result'):
                    return result.result
                else:
                    return str(result)
                    
        except Exception as e:
            Utils.log_error(e, "CrewAI default")
        
        # Strategy 3: Fallback to simple search
        Utils.log_info("Falling back to simple search")
        return simple_research(query)
        
    except Exception as e:
        Utils.log_error(e, "run_research")
        return f"Research error: {str(e)}"

def test_search_tool() -> Optional[str]:
    """Test the search tool independently"""
    try:
        tool = DuckDuckGoSearchTool()
        result = tool._run("artificial intelligence")
        Utils.log_info("Search tool test successful!")
        return result
    except Exception as e:
        Utils.log_error(e, "test_search_tool")
        return None

if __name__ == "__main__":
    # Test the search tool
    print("Testing search tool...")
    test_result = test_search_tool()
    if test_result:
        print("✅ Search tool working")
        print(Utils.truncate_text(test_result, 200))
    else:
        print("❌ Search tool failed")
    
    # Test research
    print("\nTesting research...")
    result = run_research("What is Python programming?")
    print(Utils.truncate_text(result, 500))