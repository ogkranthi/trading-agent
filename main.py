"""
Trading Analysis Multi-Agent System

A multi-agent scenario using Microsoft Agent Framework with Microsoft Foundry (Azure AI Foundry).

This system uses 4 specialized sub-agents:
- Market Agent: Technical analysis and market trends
- Fundamentals Agent: Financial statement and valuation analysis
- News Agent: News aggregation and impact assessment
- Sentiment Agent: Market psychology and social sentiment

An Orchestrator agent synthesizes all analyses into a final investment recommendation.

Usage:
    python main.py "AAPL"
    python main.py "NVIDIA Corporation"
    python main.py "Bitcoin"
"""

import asyncio
import sys

from workflow import run_analysis


def print_usage():
    """Print usage instructions."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║     Trading Analysis Multi-Agent System                        ║
║     Powered by Microsoft Agent Framework & Azure AI Foundry    ║
╚════════════════════════════════════════════════════════════════╝

Usage:
    python main.py <query>

Examples:
    python main.py "AAPL"
    python main.py "Microsoft Corporation"
    python main.py "Tesla stock analysis"
    python main.py "Bitcoin cryptocurrency"

Prerequisites:
    1. Set up Microsoft Foundry project in Azure Portal
    2. Deploy a model (e.g., gpt-4o)
    3. Copy .env.example to .env and configure:
       - FOUNDRY_PROJECT_ENDPOINT
       - MODEL_DEPLOYMENT_NAME
    4. Login with Azure CLI: az login
""")


async def main():
    """Main entry point for the trading analysis system."""
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Join all arguments as the query (handles multi-word inputs)
    query = " ".join(sys.argv[1:])
    
    if query.lower() in ["--help", "-h", "help"]:
        print_usage()
        sys.exit(0)
    
    try:
        # Run the multi-agent analysis
        result = await run_analysis(query)
        
        print("\n" + "="*60)
        print("📋 ANALYSIS COMPLETE")
        print("="*60)
        print(f"\nThe full recommendation has been printed above.")
        print("="*60)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease ensure your .env file is configured correctly.")
        print("See .env.example for the required variables.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
