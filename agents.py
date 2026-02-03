"""
Trading Analysis Multi-Agent System

This module defines specialized agents for comprehensive trading analysis:
- MarketAgentExecutor: Technical analysis and market trends
- FundamentalsAgentExecutor: Financial statement and valuation analysis
- NewsAgentExecutor: News aggregation and impact analysis
- SentimentAgentExecutor: Social sentiment and market psychology

Each agent is an Executor that wraps a ChatAgent from Microsoft Foundry.
"""

from agent_framework import (
    ChatAgent,
    ChatMessage,
    Executor,
    Role,
    WorkflowContext,
    handler,
)
from typing_extensions import Never


class MarketAgentExecutor(Executor):
    """
    Market Analysis Agent - Specializes in technical analysis and market data.
    
    Analyzes:
    - Price trends and patterns
    - Technical indicators (RSI, MACD, Moving Averages)
    - Volume analysis
    - Support and resistance levels
    """

    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id: str = "market_agent"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def analyze_market(
        self, query: str, ctx: WorkflowContext[dict]
    ) -> None:
        """
        Perform technical market analysis for the given stock/asset query.
        Sends structured analysis to the orchestrator.
        """
        message = ChatMessage(
            role=Role.USER,
            text=f"""Analyze the following from a technical/market perspective: {query}
            
            Provide your analysis in a structured format covering:
            1. Current price action and trend
            2. Key technical indicators
            3. Support/resistance levels
            4. Volume analysis
            5. Short-term and medium-term outlook"""
        )
        
        response = await self.agent.run([message])
        analysis_text = response.messages[-1].contents[-1].text if response.messages else "No analysis available"
        
        print(f"\n📊 Market Agent Analysis:\n{analysis_text[:500]}...")
        
        # Send structured result downstream
        await ctx.send_message({
            "agent": "market",
            "query": query,
            "analysis": analysis_text
        })


class FundamentalsAgentExecutor(Executor):
    """
    Fundamentals Analysis Agent - Specializes in financial analysis.
    
    Analyzes:
    - Revenue and earnings trends
    - Balance sheet strength
    - Valuation metrics (P/E, P/B, DCF)
    - Competitive positioning
    - Management quality
    """

    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id: str = "fundamentals_agent"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def analyze_fundamentals(
        self, query: str, ctx: WorkflowContext[dict]
    ) -> None:
        """
        Perform fundamental analysis for the given stock/asset query.
        Sends structured analysis to the orchestrator.
        """
        message = ChatMessage(
            role=Role.USER,
            text=f"""Analyze the following from a fundamental/financial perspective: {query}
            
            Provide your analysis in a structured format covering:
            1. Revenue and earnings analysis
            2. Balance sheet health
            3. Valuation metrics and fair value estimate
            4. Competitive advantages (moat)
            5. Key risks and opportunities"""
        )
        
        response = await self.agent.run([message])
        analysis_text = response.messages[-1].contents[-1].text if response.messages else "No analysis available"
        
        print(f"\n📈 Fundamentals Agent Analysis:\n{analysis_text[:500]}...")
        
        await ctx.send_message({
            "agent": "fundamentals",
            "query": query,
            "analysis": analysis_text
        })


class NewsAgentExecutor(Executor):
    """
    News Analysis Agent - Specializes in news and events analysis.
    
    Analyzes:
    - Recent news and press releases
    - Regulatory developments
    - Industry trends
    - Macro-economic factors
    - Upcoming catalysts
    """

    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id: str = "news_agent"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def analyze_news(
        self, query: str, ctx: WorkflowContext[dict]
    ) -> None:
        """
        Analyze news and events for the given stock/asset query.
        Sends structured analysis to the orchestrator.
        """
        message = ChatMessage(
            role=Role.USER,
            text=f"""Analyze news and events for: {query}
            
            Provide your analysis in a structured format covering:
            1. Recent significant news and developments
            2. Industry and sector trends
            3. Regulatory or policy changes
            4. Upcoming events and catalysts
            5. Potential impact on the investment thesis"""
        )
        
        response = await self.agent.run([message])
        analysis_text = response.messages[-1].contents[-1].text if response.messages else "No analysis available"
        
        print(f"\n📰 News Agent Analysis:\n{analysis_text[:500]}...")
        
        await ctx.send_message({
            "agent": "news",
            "query": query,
            "analysis": analysis_text
        })


class SentimentAgentExecutor(Executor):
    """
    Sentiment Analysis Agent - Specializes in market psychology and sentiment.
    
    Analyzes:
    - Social media sentiment
    - Analyst ratings and changes
    - Institutional activity
    - Retail investor sentiment
    - Fear and greed indicators
    """

    agent: ChatAgent

    def __init__(self, agent: ChatAgent, id: str = "sentiment_agent"):
        self.agent = agent
        super().__init__(id=id)

    @handler
    async def analyze_sentiment(
        self, query: str, ctx: WorkflowContext[dict]
    ) -> None:
        """
        Analyze market sentiment for the given stock/asset query.
        Sends structured analysis to the orchestrator.
        """
        message = ChatMessage(
            role=Role.USER,
            text=f"""Analyze market sentiment for: {query}
            
            Provide your analysis in a structured format covering:
            1. Overall sentiment score (bullish/bearish/neutral)
            2. Social media and retail investor sentiment
            3. Analyst consensus and recent rating changes
            4. Institutional investor activity
            5. Contrarian indicators and crowd psychology"""
        )
        
        response = await self.agent.run([message])
        analysis_text = response.messages[-1].contents[-1].text if response.messages else "No analysis available"
        
        print(f"\n💭 Sentiment Agent Analysis:\n{analysis_text[:500]}...")
        
        await ctx.send_message({
            "agent": "sentiment",
            "query": query,
            "analysis": analysis_text
        })


class OrchestratorAgentExecutor(Executor):
    """
    Orchestrator Agent - Synthesizes analysis from all sub-agents.
    
    Responsibilities:
    - Collects analysis from Market, Fundamentals, News, and Sentiment agents
    - Weighs different factors based on market conditions
    - Provides unified investment recommendation
    - Assigns confidence score to the recommendation
    """

    agent: ChatAgent
    collected_analyses: dict
    expected_agents: set

    def __init__(self, agent: ChatAgent, id: str = "orchestrator"):
        self.agent = agent
        self.collected_analyses = {}
        self.expected_agents = {"market", "fundamentals", "news", "sentiment"}
        super().__init__(id=id)

    @handler
    async def collect_analysis(
        self, analysis_result: dict, ctx: WorkflowContext[Never, str]
    ) -> None:
        """
        Collect analysis from sub-agents and synthesize when all are received.
        """
        agent_name = analysis_result.get("agent", "unknown")
        self.collected_analyses[agent_name] = analysis_result
        
        print(f"\n🔄 Orchestrator received analysis from: {agent_name}")
        
        # Check if all analyses have been collected
        received_agents = set(self.collected_analyses.keys())
        if received_agents >= self.expected_agents:
            await self._synthesize_recommendation(ctx)

    async def _synthesize_recommendation(
        self, ctx: WorkflowContext[Never, str]
    ) -> None:
        """
        Synthesize all collected analyses into a final recommendation.
        """
        # Compile all analyses into a prompt
        analyses_summary = "\n\n".join([
            f"=== {name.upper()} ANALYSIS ===\n{data['analysis']}"
            for name, data in self.collected_analyses.items()
        ])
        
        query = self.collected_analyses.get("market", {}).get("query", "Unknown")
        
        synthesis_prompt = ChatMessage(
            role=Role.USER,
            text=f"""As the Lead Investment Analyst, synthesize the following analyses for: {query}

{analyses_summary}

Provide a comprehensive investment recommendation including:
1. **Executive Summary**: One-paragraph overview
2. **Bull Case**: Key reasons to be bullish
3. **Bear Case**: Key reasons to be cautious
4. **Risk Assessment**: Major risks to monitor
5. **Recommendation**: BUY / HOLD / SELL with confidence level (1-10)
6. **Price Target**: If applicable
7. **Key Catalysts**: What to watch for

Be balanced and consider all perspectives from the specialized analyses."""
        )
        
        response = await self.agent.run([synthesis_prompt])
        final_recommendation = response.messages[-1].contents[-1].text if response.messages else "Unable to generate recommendation"
        
        print(f"\n{'='*60}")
        print("🎯 FINAL INVESTMENT RECOMMENDATION")
        print(f"{'='*60}")
        print(final_recommendation)
        print(f"{'='*60}\n")
        
        # Yield the final output
        await ctx.yield_output(final_recommendation)


class DispatcherExecutor(Executor):
    """
    Dispatcher - Receives user query and fans out to all analysis agents.
    
    This executor implements the fan-out pattern by sending the same
    query to all specialized analysis agents concurrently.
    """

    def __init__(self, id: str = "dispatcher"):
        super().__init__(id=id)

    @handler
    async def dispatch(
        self, 
        query: str, 
        ctx: WorkflowContext[str]
    ) -> None:
        """
        Dispatch the user's query to all analysis agents.
        Uses ctx.send_message to fan out to connected agents.
        """
        print(f"\n🚀 Dispatching analysis request: {query}")
        print("-" * 50)
        
        # Send the query to all connected downstream agents
        # The workflow edges determine which agents receive this
        await ctx.send_message(query)
