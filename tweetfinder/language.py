import py3langid as langid


def detect_most_likely(text: str) -> str:
    return langid.classify(text)[0]

