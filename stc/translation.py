from translate import Translator

class NameTranslator:
    def __init__(self, to_lang="en", from_lang="ru"):
        self.translator = Translator(to_lang=to_lang, from_lang=from_lang)

    def translate_name(self, name):
        translation = self.translator.translate(name)
        return translation