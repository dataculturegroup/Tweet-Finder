import tweetfinder.language as language


class TestLanguage:
    def test_language_en(self):
        should_be_end = language.detect_most_likely("This is a test")
        assert should_be_end == "en"

    def test_language_es(self):
        should_be_es = language.detect_most_likely("Hola como estas")
        assert should_be_es == "es"

    def test_language_de(self):
        should_be_de = language.detect_most_likely("Wie gehts")
        assert should_be_de == "de"
