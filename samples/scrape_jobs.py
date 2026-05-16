#!/usr/bin/env python3
"""
Example: Search for jobs and scrape job details
"""
import asyncio
from linkedin_scraper.scrapers.job_search import JobSearchScraper
from linkedin_scraper.scrapers.job import JobScraper
from linkedin_scraper.core.browser import BrowserManager
from linkedin_scraper.core.exceptions import RateLimitError, ScrapingError


async def main():
    """Search for jobs and scrape details"""
    
    async with BrowserManager(headless=False, slow_mo=50, user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36") as browser:
        await browser.load_session("linkedin_session.json")
        print("✓ Session loaded")
        
        # Search for jobs
        search_scraper = JobSearchScraper(browser.page)
        print("🔍 Searching for jobs...")
        job_urls = await search_scraper.search(
            keywords="software engineer",
            location="Toronto",
            limit=5
        )
        
        print(f"\n✓ Found {len(job_urls)} jobs")
        for url in job_urls:
            print(f"  - {url}")
        
        # Scrape job details if any found
        if job_urls:
            print(f"\n📄 Scraping job details...")
            job_scraper = JobScraper(browser.page)
            for i, job_url in enumerate(job_urls, start=1):
                try:
                    job = await job_scraper.scrape(job_url)

                    print("\n" + "="*60)
                    print(f"Job #{i}: {job_url}")
                    print(f"Title: {job.job_title}")
                    print(f"Company: {job.company}")
                    print(f"Location: {job.location}")
                    print(f"Posted: {job.posted_date}")
                    print(f"Applicants: {job.applicant_count}")
                    print(f"Description: {job.job_description[:200]}..." if job.job_description else "Description: N/A")
                    print("="*60)
                except RateLimitError as e:
                    print("\n⚠️ Rate limited while scraping job:", e)
                    try:
                        await browser.page.screenshot(path=f"debug_job_{i}.png", full_page=True)
                        html = await browser.page.content()
                        with open(f"debug_job_{i}.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        print(f"Saved debug_job_{i}.png and debug_job_{i}.html")
                    except Exception as err:
                        print("Could not save debug artifacts:", err)
                except ScrapingError as e:
                    print("\n❌ Scraping failed for job:", e)
    
    print("\n✓ Done!")


if __name__ == "__main__":
    asyncio.run(main())
