from mcp.server.fastmcp import FastMCP
from requests import get
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


mcp = FastMCP("cog")

@mcp.tool()
async def get_context(url: str):
    """Get relevant tech context to the query.

    Args:
        url: a sitemap url (ex: https://modelcontextprotocol.io/sitemap.xml)
    
    """
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/scrape/get_context?url={url}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return f"Error retrieving context: {str(e)}"




if __name__ == "__main__":
    mcp.run(transport='stdio')