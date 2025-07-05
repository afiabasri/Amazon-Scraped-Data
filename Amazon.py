from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def scrape_amazon_products(base_url, max_pages=8):
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()

        for page_num in range(1, max_pages + 1):
            print(f"\n🔄 Scraping page {page_num}")
            url = f"{base_url}&page={page_num}"
            page.goto(url, timeout=60000)
            page.wait_for_selector("div.s-main-slot", timeout=15000)
            soup = BeautifulSoup(page.content(), "html.parser")
            
            results = soup.select("div.s-main-slot > div[data-component-type='s-search-result']")

            for result in results:
                # Title
                title_tag = result.select_one("h2 span")
                title = title_tag.text.strip() if title_tag else "N/A"

                # Link
                link_tag = result.select_one("a")
                if link_tag and link_tag.get("href"):
                    link = "https://www.amazon.com" + link_tag["href"]
                else:
                    link = "N/A"

                # Price
                price_tag = result.select_one("span.a-price > span.a-offscreen")
                price = price_tag.text.strip() if price_tag else "N/A"

                # Rating
                rating_tag = result.select_one("span.a-icon-alt")
                rating = rating_tag.text.strip() if rating_tag else "N/A"

                # Reviews 
                reviews_tag = result.select_one("span[aria-label$='ratings']")
                if not reviews_tag:
                    reviews_tag = result.select_one("span[aria-label$='rating']")
                    if not reviews_tag:
                        reviews_tag = result.select_one("div.a-row.a-size-small span.a-size-base")
                        reviews = reviews_tag.text.strip() if reviews_tag else "N/A"


                data.append({
                    "Title": title,
                    "Price": price,
                    "Rating": rating,
                    "Reviews": reviews,
                    "Link": link
                })

        browser.close()
    return data


base_url = "https://www.amazon.com/s?k=watches+for+women+digital+under+40"
products = scrape_amazon_products(base_url, max_pages=8)

# Save to Excel
df = pd.DataFrame(products)
df.to_excel("Amazon_watches_full.xlsx", index=False)
print("✅ Data saved to 'Amazon_watches_full.xlsx'")







