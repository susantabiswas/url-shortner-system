import secrets


# Class that handles the workflows of URL shortener
class UrlShortenerWorkflow:
    # Contains possible chars: a-zA-Z0-9
    char_set: str = ""

    def __init__(self):
        # A-Z
        for ch in range(ord('A'), ord('A') + 26):
            UrlShortenerWorkflow.char_set += chr(ch)

        # a-z
        for ch in range(ord('a'), ord('a') + 26):
            UrlShortenerWorkflow.char_set += chr(ch)

        # 0-9
        for ch in range(ord('0'), ord('0') + 10):
            UrlShortenerWorkflow.char_set += chr(ch)

    # Generates a hash key of desired length
    async def generate_hash_key(len: int = 6):
        return "".join(secrets.choice(
                UrlShortenerWorkflow.char_set) for _ in range(6)
            )
