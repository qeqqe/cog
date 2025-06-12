from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator
import asyncio
from xml.etree import ElementTree as ET
from typing import List
import httpx

async def crawl_sequentially(url: str) -> dict:
    """Crawls a url sitemap's every page sequentially and returns the content
    Args:
        url (str): The URL of the sitemap to crawl.
    """
    try:
        urls = await get_sitemap_urls(url)
        if not urls:
            return {"error": "No URLs found in the sitemap."}
    
        print("------===Starting Sequential Crawling===------")
        
        browser_config = BrowserConfig(headless=True, extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"])

        crawl_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator()
        )
        
        crawler = AsyncWebCrawler(config=browser_config)
        DATA=[]
        
        session_id="session1"
        for url in urls:
            print(f"Crawling URL: {url}")
            try:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id=session_id  
                )
                if result.success:
                    DATA.append(result.markdown.raw_markdown)
                    print(f"Successfully crawled {url}, url len= {len(result.markdown.raw_markdown)}")
            except Exception as e:
                print(f"Error crawling {url}: {e}")
        print("------===Finished Sequential Crawling===------")
        return {"data": DATA}
        
    except:
        return {"error": "Couldn't fetch the sitemap pages."}
        


async def get_sitemap_urls(sitemap_url: str) -> List[str]:
    """Crawls a sitemap and returns the url of every page in the sitemap.
    Args:
        sitemap_url (str): The URL of the sitemap to crawl.
    Returns:
        List[str]: A list of URLs found in the sitemap.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(sitemap_url)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
            return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []
