from langchain_core.tools import tool
from mcp import StdioServerParameters
from langchain_mcp_adapters.client import MultiServerMCPClient

@tool
def get_live_stock_price(ticker: str) -> str:
    """
    Fetches the current real-time stock price for a given ticker symbol.
    Call this whenever the user asks for a stock price.
    """
    # Mock data
    mock_prices = {"AAPL": 150.0, "TSLA": 200.0, "MSFT": 400.0}
    if ticker.upper() in mock_prices:
        return f"The current price of {ticker} is ${mock_prices[ticker.upper()]}"
    return f"Sorry, I could not find the price for {ticker}."

async def get_mcp_tools():
    """
    Connects to the MCP server and returns its tools as LangChain tools.
    For demonstration, this connects to the public @modelcontextprotocol/server-everything server via npx.
    """
    # Example MCP server params
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"]
    )
    
    try:
        client = MultiServerMCPClient()
        await client.connect_server("everything_server", server_params)
        return client.get_tools()
    except Exception as e:
        import logging
        logging.error(f"Failed to connect to MCP: {e}")
        return []
