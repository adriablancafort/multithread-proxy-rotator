def get_proxies() -> list[str]:
    """Return the list of proxies."""
    with open("proxies.txt", "r") as file:
        return [f"http://{line.strip()}" for line in file]


def store_product(product: str) -> None:
    """Store the product in a file."""
    with open("output.txt", "a") as file:
        file.write(f"{product}\n")


def amazon_asin_generator():
    """Amazon ASINs generator."""
    with open("asins.txt", "r") as file:
        for line in file:
            yield line.strip()
