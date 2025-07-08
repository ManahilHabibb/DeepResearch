````markdown
# 🔍 AI Research Assistant

A powerful AI-powered research assistant that uses CrewAI agents to search the web, analyze information, and generate comprehensive reports.

## Features

- 🌐 Web search using DuckDuckGo
- 🤖 Multi-agent AI research system
- 📊 Structured report generation
- 💬 Interactive Streamlit interface
- 🔌 MCP server support
- 🎯 Comprehensive source citations

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ai-research-assistant
   python setup.py
   ```
````

2. **Run the Application**

   ```bash
   streamlit run app.py
   ```

3. **Access the Interface**
   - Open browser to: http://localhost:8501
   - Start asking research questions!

## Configuration

### Optional: OpenAI API Key

For better performance, add your OpenAI API key to `.env`:

```
OPENAI_API_KEY=your_api_key_here
```

### Alternative: Use Ollama (Local LLM)

Install and run Ollama for local AI processing:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

## Usage Examples

- "What is quantum computing?"
- "Latest developments in AI"
- "Climate change impact 2024"
- "Cryptocurrency market trends"

## Troubleshooting

- **LLM Errors**: App automatically falls back to simple search mode
- **Search Issues**: Check internet connection and DuckDuckGo availability
- **Dependencies**: Run `pip install -r requirements.txt`

## License

MIT License

```

```
