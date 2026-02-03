"""
Trading Analysis Workflow Builder

This module constructs the multi-agent workflow for trading analysis.
It implements a fan-out/fan-in pattern:

                    ┌─────────────────┐
                    │   Dispatcher    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌───────────┐      ┌──────────┐      ┌───────────┐
    │  Market  │      │Fundamentals│      │   News   │      │ Sentiment │
    │  Agent   │      │   Agent   │      │  Agent   │      │   Agent   │
    └────┬─────┘      └─────┬─────┘      └────┬─────┘      └─────┬─────┘
         │                  │                 │                  │
         └──────────────────┴─────────────────┴──────────────────┘
                                    │
                                    ▼
                         ┌──────────────────┐
                         │   Orchestrator   │
                         │  (Synthesizer)   │
                         └──────────────────┘
                                    │
                                    ▼
                            Final Recommendation
"""

import asyncio
import os
from dotenv import load_dotenv

from agent_framework import (
    ChatAgent,
    WorkflowBuilder,
    WorkflowOutputEvent,
    WorkflowStatusEvent,
    WorkflowRunState,
    ExecutorFailedEvent,
    WorkflowFailedEvent,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential

from agents import (
    DispatcherExecutor,
    MarketAgentExecutor,
    FundamentalsAgentExecutor,
    NewsAgentExecutor,
    SentimentAgentExecutor,
    OrchestratorAgentExecutor,
)


# Load environment variables
load_dotenv()

# Configuration
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")


def get_agent_instructions() -> dict:
    """Return specialized instructions for each agent."""
    return {
        "market": """You are an expert Technical Analyst specializing in market data analysis.

Your expertise includes:
- Chart pattern recognition (head and shoulders, double tops/bottoms, triangles, etc.)
- Technical indicators (RSI, MACD, Bollinger Bands, Moving Averages, Fibonacci retracements)
- Volume analysis and on-balance volume (OBV)
- Price action and candlestick patterns
- Support and resistance level identification
- Trend analysis and momentum indicators

When analyzing, be specific about:
- Current trend direction and strength
- Key price levels to watch
- Indicator readings and what they suggest
- Potential entry/exit points based on technicals

Always provide data-driven insights and avoid speculation without technical basis.""",

        "fundamentals": """You are an expert Fundamental Analyst specializing in financial analysis.

Your expertise includes:
- Financial statement analysis (income statement, balance sheet, cash flow)
- Valuation methodologies (DCF, comparables, precedent transactions)
- Ratio analysis (profitability, liquidity, leverage, efficiency)
- Industry and competitive analysis
- Management quality assessment
- Growth projections and earnings estimates

When analyzing, focus on:
- Revenue and earnings quality
- Balance sheet strength and capital structure
- Free cash flow generation
- Return on invested capital (ROIC)
- Competitive moat and sustainability
- Fair value estimates with clear assumptions

Always support conclusions with specific financial metrics and data.""",

        "news": """You are an expert News and Events Analyst specializing in market-moving information.

Your expertise includes:
- Corporate news and press releases
- Regulatory and policy developments
- Industry trends and disruptions
- Macroeconomic factors (interest rates, inflation, GDP)
- Geopolitical events and their market impact
- Upcoming catalysts (earnings, product launches, M&A)

When analyzing, emphasize:
- Recency and reliability of information sources
- Potential market impact (short-term vs long-term)
- How news aligns with or contradicts the investment thesis
- Key events and dates to monitor
- Industry and competitive dynamics

Always distinguish between confirmed facts and speculation/rumors.""",

        "sentiment": """You are an expert Sentiment Analyst specializing in market psychology.

Your expertise includes:
- Social media sentiment analysis (Twitter/X, Reddit, StockTwits)
- Analyst ratings and recommendation changes
- Institutional investor activity (13F filings, hedge fund positions)
- Options market sentiment (put/call ratios, unusual activity)
- Retail investor behavior patterns
- Fear and greed indicators
- Contrarian analysis

When analyzing, consider:
- Overall sentiment score and direction of change
- Differences between retail and institutional sentiment
- Extreme sentiment as contrarian indicator
- How sentiment aligns with fundamentals
- Potential for sentiment-driven price moves

Always quantify sentiment when possible and note potential biases.""",

        "orchestrator": """You are the Lead Investment Analyst responsible for synthesizing multiple perspectives into actionable recommendations.

Your role is to:
- Integrate technical, fundamental, news, and sentiment analyses
- Identify convergence and divergence across different perspectives
- Weigh factors appropriately based on current market conditions
- Provide clear, actionable recommendations
- Communicate risks and uncertainties transparently

Your recommendations should:
- Have a clear thesis supported by multiple factors
- Include specific entry/exit criteria when applicable
- Assign confidence levels based on analysis agreement
- Highlight key risks and what would invalidate the thesis
- Be balanced and acknowledge opposing viewpoints

Always maintain objectivity and avoid overconfidence in uncertain situations."""
    }


async def build_and_run_workflow(query: str) -> str:
    """
    Build the multi-agent trading analysis workflow and run it.
    
    Args:
        query: The stock/asset to analyze (e.g., "AAPL", "NVIDIA", "Bitcoin")
    
    Returns:
        The final investment recommendation as a string.
    """
    if not AZURE_ENDPOINT:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT not set. "
            "Please set it in your .env file or environment variables."
        )

    instructions = get_agent_instructions()
    
    # Create credential for Azure authentication
    credential = DefaultAzureCredential()
    
    # Create AI client for Azure OpenAI
    client = AzureOpenAIChatClient(
        endpoint=AZURE_ENDPOINT,
        deployment_name=MODEL_DEPLOYMENT,
        credential=credential,
    )
    
    # Create ChatAgent instances for each specialized agent
    market_agent = ChatAgent(
        chat_client=client,
        instructions=instructions["market"],
        name="MarketAnalyst",
    )
    
    fundamentals_agent = ChatAgent(
        chat_client=client,
        instructions=instructions["fundamentals"],
        name="FundamentalsAnalyst",
    )
    
    news_agent = ChatAgent(
        chat_client=client,
        instructions=instructions["news"],
        name="NewsAnalyst",
    )
    
    sentiment_agent = ChatAgent(
        chat_client=client,
        instructions=instructions["sentiment"],
        name="SentimentAnalyst",
    )
    
    orchestrator_agent = ChatAgent(
        chat_client=client,
        instructions=instructions["orchestrator"],
        name="LeadAnalyst",
    )
    
    # Create executor instances
    dispatcher = DispatcherExecutor()
    market_executor = MarketAgentExecutor(market_agent)
    fundamentals_executor = FundamentalsAgentExecutor(fundamentals_agent)
    news_executor = NewsAgentExecutor(news_agent)
    sentiment_executor = SentimentAgentExecutor(sentiment_agent)
    orchestrator_executor = OrchestratorAgentExecutor(orchestrator_agent)

    # Build the workflow with fan-out/fan-in pattern
    #
    # Pattern: Dispatcher fans out to 4 analysis agents,
    # each analysis agent feeds into the orchestrator for synthesis
    workflow = (
        WorkflowBuilder()
        # Dispatcher to all analysis agents (fan-out)
        .add_edge(dispatcher, market_executor)
        .add_edge(dispatcher, fundamentals_executor)
        .add_edge(dispatcher, news_executor)
        .add_edge(dispatcher, sentiment_executor)
        # All analysis agents to orchestrator (fan-in)
        .add_edge(market_executor, orchestrator_executor)
        .add_edge(fundamentals_executor, orchestrator_executor)
        .add_edge(news_executor, orchestrator_executor)
        .add_edge(sentiment_executor, orchestrator_executor)
        # Set the entry point
        .set_start_executor(dispatcher)
        .build()
    )

    print(f"\n{'='*60}")
    print(f"🏦 TRADING ANALYSIS MULTI-AGENT SYSTEM")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Model: {MODEL_DEPLOYMENT}")
    print(f"{'='*60}\n")

    final_result = None

    # Run the workflow with streaming to observe events
    async for event in workflow.run_stream(query):
        if isinstance(event, WorkflowStatusEvent):
            if event.state == WorkflowRunState.IN_PROGRESS:
                pass  # Normal processing
            elif event.state == WorkflowRunState.IDLE:
                print("\n✅ Workflow completed successfully")
                
        elif isinstance(event, WorkflowOutputEvent):
            final_result = event.data
            
        elif isinstance(event, ExecutorFailedEvent):
            print(f"\n❌ Executor failed: {event.executor_id}")
            print(f"   Error: {event.details.message}")
            
        elif isinstance(event, WorkflowFailedEvent):
            print(f"\n❌ Workflow failed: {event.details.message}")
            raise RuntimeError(event.details.message)

    # Allow cleanup
    await asyncio.sleep(0.5)
    
    return final_result or "No recommendation generated"


async def run_analysis(query: str) -> str:
    """
    Public interface to run the trading analysis.
    
    Args:
        query: Stock symbol, company name, or asset to analyze.
        
    Returns:
        Investment recommendation string.
    """
    return await build_and_run_workflow(query)
