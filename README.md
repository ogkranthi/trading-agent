# Trading Analysis Multi-Agent System

A sophisticated multi-agent trading analysis system built with **Microsoft Agent Framework** and **Microsoft Foundry (Azure AI Foundry)**.

## Architecture

This system implements a **fan-out/fan-in** multi-agent pattern with 4 specialized analysis agents and an orchestrator:

```
                    ┌─────────────────┐
                    │   Dispatcher    │
                    │  (Entry Point)  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼                  ▼
    ┌──────────┐      ┌───────────┐      ┌──────────┐      ┌───────────┐
    │  Market  │      │Fundamentals│     │   News   │      │ Sentiment │
    │  Agent   │      │   Agent   │      │  Agent   │      │   Agent   │
    └────┬─────┘      └─────┬─────┘      └────┬─────┘      └─────┬─────┘
         │                  │                 │                  │
         └──────────────────┴─────────────────┴──────────────────┘
                                    │
                                    ▼
                         ┌──────────────────┐
                         │   Orchestrator   │
                         │  (Lead Analyst)  │
                         └──────────────────┘
                                    │
                                    ▼
                         Investment Recommendation
```

## Agents

### 1. Market Agent (Technical Analysis)
- Price trends and patterns
- Technical indicators (RSI, MACD, Moving Averages)
- Support and resistance levels
- Volume analysis

### 2. Fundamentals Agent (Financial Analysis)
- Revenue and earnings analysis
- Balance sheet health
- Valuation metrics (P/E, DCF, etc.)
- Competitive moat assessment

### 3. News Agent (Events Analysis)
- Recent news and developments
- Regulatory changes
- Industry trends
- Upcoming catalysts

### 4. Sentiment Agent (Market Psychology)
- Social media sentiment
- Analyst ratings
- Institutional activity
- Contrarian indicators

### 5. Orchestrator (Lead Analyst)
- Synthesizes all agent analyses
- Provides unified recommendation
- Assigns confidence levels
- Highlights key risks

## Prerequisites

1. **Azure Subscription** with access to Microsoft Foundry
2. **Python 3.10+**
3. **Azure CLI** installed and logged in (`az login`)

## Setup

### 1. Install Dependencies

```bash
# Note: --pre flag is required while Agent Framework is in preview
pip install -r requirements.txt --pre
```

### 2. Configure Microsoft Foundry

1. Create a Microsoft Foundry project in [Azure Portal](https://portal.azure.com)
2. Deploy a model (recommended: `gpt-4o` or `gpt-5-mini`)
3. Copy the project endpoint and model deployment name

### 3. Set Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values:
# FOUNDRY_PROJECT_ENDPOINT=https://your-project.api.azureml.ms
# MODEL_DEPLOYMENT_NAME=gpt-4o
```

### 4. Azure Authentication

```bash
# Login to Azure (required for DefaultAzureCredential)
az login
```

## Usage

```bash
# Analyze a specific stock
python main.py "AAPL"

# Analyze with company name
python main.py "Microsoft Corporation"

# Analyze cryptocurrency
python main.py "Bitcoin"

# Multi-word queries
python main.py "Tesla stock analysis and price prediction"
```

## Sample Output

```
============================================================
🏦 TRADING ANALYSIS MULTI-AGENT SYSTEM
============================================================
Query: AAPL
Model: gpt-4o
============================================================

🚀 Dispatching analysis request: AAPL
--------------------------------------------------

📊 Market Agent Analysis:
[Technical analysis of price trends, indicators, etc.]

📈 Fundamentals Agent Analysis:
[Financial metrics, valuation, competitive analysis]

📰 News Agent Analysis:
[Recent developments, catalysts, industry trends]

💭 Sentiment Agent Analysis:
[Social sentiment, analyst ratings, institutional activity]

🔄 Orchestrator received analysis from: market
🔄 Orchestrator received analysis from: fundamentals
🔄 Orchestrator received analysis from: news
🔄 Orchestrator received analysis from: sentiment

============================================================
🎯 FINAL INVESTMENT RECOMMENDATION
============================================================
[Comprehensive recommendation with BUY/HOLD/SELL rating,
 confidence level, price target, and key catalysts]
============================================================
```

## Project Structure

```
trading-agent/
├── main.py              # Entry point
├── agents.py            # Agent executor definitions
├── workflow.py          # Workflow builder and orchestration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
└── README.md            # This file
```

## Key Concepts

### Microsoft Agent Framework
- **Executor**: A unit of work in the workflow (each agent is an Executor)
- **WorkflowBuilder**: Fluent API to define agent connections
- **WorkflowContext**: Enables message passing between agents
- **run_stream()**: Async streaming for real-time event observation

### Multi-Agent Patterns Used
- **Fan-out**: Dispatcher sends query to all analysis agents simultaneously
- **Fan-in**: Orchestrator collects results from all agents
- **Streaming**: Real-time observation of workflow progress

## Extending the System

### Adding a New Agent

1. Create a new `Executor` subclass in `agents.py`:

```python
class NewAgentExecutor(Executor):
    agent: ChatAgent
    
    def __init__(self, agent: ChatAgent, id: str = "new_agent"):
        self.agent = agent
        super().__init__(id=id)
    
    @handler
    async def analyze(self, query: str, ctx: WorkflowContext[dict]) -> None:
        # Your analysis logic
        await ctx.send_message({"agent": "new", "analysis": result})
```

2. Add instructions in `workflow.py`:

```python
"new_agent": """Your specialized instructions here..."""
```

3. Wire into the workflow in `build_and_run_workflow()`:

```python
.add_edge(dispatcher, new_executor)
.add_edge(new_executor, orchestrator_executor)
```

## Troubleshooting

### "FOUNDRY_PROJECT_ENDPOINT not set"
Ensure your `.env` file exists and contains the correct endpoint:
```
FOUNDRY_PROJECT_ENDPOINT=https://your-project.api.azureml.ms
```

### Authentication Errors
Run `az login` to refresh your Azure credentials.

### Model Deployment Errors
Verify your model is deployed in Microsoft Foundry and the name matches `MODEL_DEPLOYMENT_NAME`.

## Resources

- [Microsoft Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [Microsoft Foundry (Azure AI Foundry)](https://azure.microsoft.com/products/ai-foundry/)
- [Azure Identity Documentation](https://docs.microsoft.com/azure/developer/python/sdk/authentication)

## License

MIT License
