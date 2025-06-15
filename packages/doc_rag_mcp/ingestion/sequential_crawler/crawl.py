from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator
import asyncio
from xml.etree import ElementTree as ET
from typing import List, AsyncGenerator, Dict, Any
import httpx
import logging
from ..chunker.chunker import chunk_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_sequentially(url: str) -> dict:
    """Crawls a url sitemap's every page sequentially and return the crawling results.
    Args:
        url: The URL of the sitemap to crawl.
    Return:
        dict: crawling results with statistics
    """
    try:
        urls = await get_sitemap_urls(url)
        if not urls:
            return {"error": "No URLs found in the sitemap.", "success": False}
    
        logger.info(f"starting sequential crawling of {len(urls)} URLs")
        
        stats = {
            "total_urls": len(urls),
            "successful": 0,
            "failed": 0,
            "total_content_length": 0,
            "processed_urls": []
        }
        
        # process in batches to prevent any memory issues
        async for result in crawl_and_process_batch(urls):
            if result["success"]:
                stats["successful"] += 1
                stats["total_content_length"] += result["content_length"]
                stats["processed_urls"].append(result["url"])
            else:
                stats["failed"] += 1
        
        logger.info(f"Finished crawling. Success: {stats['successful']}, Failed: {stats['failed']}")
        
        return {
            "success": True,
            "message": "Crawling completed successfully",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error in crawl_sequentially: {e}")
        return {"error": f"Crawling failed: {str(e)}", "success": False}


async def crawl_and_process_batch(urls: List[str], batch_size: int = 10) -> AsyncGenerator[Dict[str, Any], None]:
    """Process Urls in batches and give results
    Args:
        urls: list of Urls to crawl
        batch_size: No. of Urls to process in each batch
    Yields:
        Dict containing crawl result for each url
    """
    browser_config = BrowserConfig(
        headless=True, 
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"]
    )
    
    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )
    
    crawler = AsyncWebCrawler(config=browser_config)
    session_id = "batch_session"
    
    try:
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
            
            for url in batch:
                logger.info(f"Crawling URL: {url}")
                try:
                    result = await crawler.arun(
                        url=url,
                        config=crawl_config,
                        session_id=session_id
                    )
                    
                    if result.success and result.markdown.raw_markdown:
                        content = result.markdown.raw_markdown
                        content_length = len(content)
                        """TODO
                        Shit to add:
                        - Semantically chunking
                        - Embedding the chunks
                        - Storing the embeddings
                        """    
                        SEMANTIC_CHUNKS = chunk_content(content)
                        logger.info(f"Semantic chunk length: {len(SEMANTIC_CHUNKS)}")
                        yield {
                            "success": True,
                            "url": url,
                            "content_length": content_length,
                            "message": f"Successfully processed {url}"
                        }
                        
                        logger.info(f"Successfully crawled {url}, content length: {content_length}")
                    else:
                        yield {
                            "success": False,
                            "url": url,
                            "error": "No content retrieved or crawl failed"
                        }
                        
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    yield {
                        "success": False,
                        "url": url,
                        "error": str(e)
                    }
                
                # avoid overwhelming/rate-limiting the server
                await asyncio.sleep(0.1)
                
    finally:
        try:
            await crawler.aclose()
        except Exception as e:
            logger.warning(f"Error closing crawler: {e}")


async def get_sitemap_urls(sitemap_url: str) -> List[str]:
    """Crawls a sitemap and returns the url of every page in the sitemap.
    Args:
        sitemap_url: The URL of the sitemap to crawl.
    Returns:
        List[str]: A list of URLs found in the sitemap.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(sitemap_url)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
            logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
    except Exception as e:
        logger.error(f"Error fetching sitemap: {e}")
        return []


if __name__ == "__main__":
    url = "https://ai.pydantic.dev/sitemap.xml"
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(crawl_sequentially(url))