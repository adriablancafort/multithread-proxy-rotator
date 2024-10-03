from database import get_proxies, amazon_asin_generator, store_product
from proxy_rotator import ProxyRotator
from selectolax.parser import HTMLParser
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from os import getenv


def parse_amazon_product(html: str) -> str:
    """Given the HTML, return the product information."""
    tree = HTMLParser(html)

    title_element = tree.css_first("h1 span")
    price_symbol_element = tree.css_first("span.a-price-symbol")
    price_whole_element = tree.css_first("span.a-price-whole")
    price_fraction_element = tree.css_first("span.a-price-fraction")

    product_title = title_element.text().strip() if title_element else "Title not found"
    price_symbol = price_symbol_element.text() if price_symbol_element else "Symbol not found"
    price_whole = price_whole_element.text().replace(".", "") if price_whole_element else "Whole part not found"
    price_fraction = price_fraction_element.text() if price_fraction_element else "Fraction not found"

    return f"{product_title} {price_symbol}{price_whole}.{price_fraction}"


def scrape_amazon_product(proxy_rotator: ProxyRotator, asin: str) -> None:
    """Given an ASIN, scrape and save the product information."""
    url = f"https://www.amazon.com/dp/{asin}"
    while True:
        html = proxy_rotator.get_content(url)
        if "Enter the characters you see below" not in html:
            print(f"{url} Success")
            break
        else:
            print(f"{url} CAPTCHA")
    product = parse_amazon_product(html)
    store_product(product)


def main() -> None:
    load_dotenv()
    username = getenv("PROXY_USERNAME")
    password = getenv("PROXY_PASSWORD")
    proxies = get_proxies(username, password)
    proxy_rotator = ProxyRotator(proxies)
    asins = amazon_asin_generator()
    num_workers = 20
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for asin in asins:
            executor.submit(scrape_amazon_product, proxy_rotator, asin)


if __name__ == "__main__":
    main()
