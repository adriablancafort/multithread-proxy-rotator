from curl_cffi import requests


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
        """Get the content of the given URL through a proxy."""
        while self.proxies:
            self._rotate_proxy()
            proxy = self.proxies[self.current_index]
            session = self.sessions[self.current_index]
            try:
                response = session.get(url, impersonate="safari", proxy=proxy, timeout=3000)
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"{url} {response.status_code}")
            except Exception as error:
                print(f"{url} {error}")
                self._remove_proxy()
        raise Exception("No proxies left")
