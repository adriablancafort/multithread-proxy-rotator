from selectolax.parser import HTMLParser
from curl_cffi import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from os import getenv


def get_proxies(username: str, password: str) -> list[str]:
    """Get a list of proxies."""
    with open("proxies.txt", "r") as file:
        return [f"http://{username}:{password}@{line.strip()}" for line in file]


def asin_generator():
    """ASINs generator."""
    with open("asins.txt", "r") as file:
        for line in file:
            yield line.strip()


def store_product(product: str) -> None:
    """Store product in a file."""
    with open("output.txt", "a") as file:
        file.write(f"{product}\n")


class ProxyRotator:
    def __init__(self, proxies: list[str]) -> None:
        self.proxies = proxies
        self.sessions = [requests.Session() for _ in proxies]
        self.current_index = 0

    def _rotate_proxy(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.proxies)

    def _remove_proxy(self) -> None:
        del self.proxies[self.current_index]
        del self.sessions[self.current_index]

    def get_content(self, url: str) -> str:
        while self.proxies:
            self._rotate_proxy()
            proxy = self.proxies[self.current_index]
            session = self.sessions[self.current_index]
            try:
                response = session.get(url, impersonate="safari", proxy=proxy)
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"{url}, {response.status_code}")
            except Exception as error:
                print(f"{url}, {error}")
                self._remove_proxy()
        raise Exception("No proxies left")

def parse_amazon_product(html: str) -> str:
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
    url = f"https://www.amazon.com/dp/{asin}"
    while True:
        html = proxy_rotator.get_content(url)
        if "Enter the characters you see below" not in html:
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
    asins = asin_generator()
    num_workers = 10
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        while True:
            try:
                asin = next(asins)
                executor.submit(scrape_amazon_product, proxy_rotator, asin)
            except StopIteration:
                break

if __name__ == "__main__":
    main()
