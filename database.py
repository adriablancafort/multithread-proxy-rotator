def get_proxies(username: str, password: str) -> list[str]:
    """Return the list of proxies."""
    with open("proxies.txt", "r") as file:
        return [f"http://{username}:{password}@{line.strip()}" for line in file]


def asin_generator():
    """ASINs generator."""
    with open("asins.txt", "r") as file:
        for line in file:
            yield line.strip()


def store_product(product: str) -> None:
    """Store the product in a file."""
    with open("output.txt", "a") as file:
        file.write(f"{product}\n")
