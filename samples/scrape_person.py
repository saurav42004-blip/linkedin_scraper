#!/usr/bin/env python3
"""
Example: Scrape a single LinkedIn profile

This example shows how to use the PersonScraper to scrape a LinkedIn profile.
"""
import asyncio
from linkedin_scraper.scrapers.person import PersonScraper
from linkedin_scraper.core.browser import BrowserManager
from linkedin_scraper.core.exceptions import RateLimitError, ScrapingError
from linkedin_scraper import wait_for_manual_login


async def main():
    """Scrape a single person profile"""
    profile_url = "https://www.linkedin.com/in/williamhgates/"

    
    # Initialize and start browser using context manager
    async with BrowserManager(
        headless=False,
        slow_mo=250,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        ) as browser:

    
        # Load existing session (must be created first - see README for setup)
        await browser.load_session("linkedin_session.json")
        print("✓ Session loaded")

        # Warm up session with gentle navigation to reduce challenge likelihood
        await browser.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Initialize scraper with the browser page
        scraper = PersonScraper(browser.page)
        
        # Scrape the profile
        print(f"🚀 Scraping: {profile_url}")
        await asyncio.sleep(2)
        try:
            person = await scraper.scrape(profile_url)
        except RateLimitError as e:
            print("\n⚠️ LinkedIn rate-limited or showed a security challenge.")
            print(f"Reason: {e}")
            print("Try again later, use a different profile, or complete manual verification in the browser.")
            return
        except ScrapingError as e:
            if "Not logged in" in str(e):
                print("\n⚠️ Session expired or invalid. Please log in manually in the opened browser...")
                await browser.page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
                try:
                    await wait_for_manual_login(browser.page, timeout=300000)
                    await browser.save_session("linkedin_session.json")
                    print("✓ Session refreshed. Retrying scrape...")
                    person = await scraper.scrape(profile_url)
                except Exception as login_err:
                    print(f"\n❌ Manual login/refresh failed: {login_err}")
                    return
            else:
                print(f"\n❌ Scraping failed: {e}")
                return
        
        # Display results
        print("\n" + "="*60)
        print(f"Name: {person.name}")
        print(f"Location: {person.location}")
        print(f"About: {person.about[:100]}..." if person.about else "About: N/A")
        print(f"Experiences: {len(person.experiences)}")
        print(f"Education: {len(person.educations)}")
        print("="*60)
        # Debug: save page screenshot and HTML if key fields missing
        if person.name in (None, "Unknown") or len(person.experiences) == 0:
            try:
                screenshot_path = "debug_profile.png"
                html_path = "debug_profile.html"
                await browser.page.screenshot(path=screenshot_path, full_page=True)
                html = await browser.page.content()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved debug artifacts: {screenshot_path}, {html_path}")
            except Exception as e:
                print(f"Could not save debug artifacts: {e}")
    
    print("\n✓ Done!")


if __name__ == "__main__":
    asyncio.run(main())
