from googletrans import Translator

def language_detector(text):
    
    translator = Translator()
    detected = translator.detect(text)
    return detected.lang

def translate_to_english(text):

    translator = Translator()
    translated = translator.translate(text, dest='en')
    return translated.text


