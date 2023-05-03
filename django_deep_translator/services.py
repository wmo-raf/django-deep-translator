import six

from django.conf import settings
from deep_translator import (GoogleTranslator, 
                            MyMemoryTranslator,
                            DeeplTranslator,
                            QcriTranslator,
                            PonsTranslator,
                            YandexTranslator,
                            MicrosoftTranslator,
                            PapagoTranslator,
                            LibreTranslator)

class BaseTranslatorService:
    """
    Defines the base methods that should be implemented
    """

    def translate_string(self,text, target_language, source_language='auto'):
        """
        Returns a single translated string literal for the target language.
        """
        raise NotImplementedError('.translate_string() must be overridden.')
    

class GoogleTranslatorService(BaseTranslatorService):


    def translate_string(self, text, target_language, source_language='auto'):
        self.service = GoogleTranslator(source=source_language, target=target_language)
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text)
    

class MyMemoryTranslatorService(BaseTranslatorService):

    def translate_string(self, text, target_language, source_language='en'):
        self.service = MyMemoryTranslator(source=source_language, target=target_language)
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text)
    
class DeeplTranslatorService(BaseTranslatorService):

    # deep-translator uses free deepl api by default. If you have the pro version then simply set the use_free_api to false

    def __init__(self):

        self.developer_key = getattr(settings, 'DEEPL_TRANSLATE_KEY', None)
        assert self.developer_key, ('`DEEPL_TRANSLATE_KEY` is not configured, '
                                    'it is required by `DeeplTranslatorService. '
                                    'Visit https://www.deepl.com/en/docs-api/ for more information on how to generate your Deepl api key')

    def translate_string(self, text, target_language, source_language='en', use_free_api=True):
        self.service = DeeplTranslator(
            source=source_language, 
            target=target_language, 
            api_key=self.developer_key,
            use_free_api=getattr(settings, 'DEEPL_FREE_API', use_free_api)
        )
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text)
    

class QcriTranslatorService(BaseTranslatorService):

    # In order to use the QcriTranslator translator, you need to generate a free api key. 

    def __init__(self):

        self.developer_key = getattr(settings, 'QCRI_TRANSLATE_KEY', None)
        assert self.developer_key, ('`QCRI_TRANSLATE_KEY` is not configured, '
                                    'it is required by `QcriTranslatorService. '
                                    'Visit https://mt.qcri.org/api/ for more information')

    def translate_string(self, text, target_language, source_language='en'):
        self.service = QcriTranslator(
            self.developer_key,
        )
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(source=source_language, 
            target=target_language, text=text, domain="news")
    

class PonsTranslatorService(BaseTranslatorService):

    def translate_string(self, text, target_language, source_language='en'):
        self.service = PonsTranslator(source=source_language, target=target_language)
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text)
    
class YandexTranslatorService(BaseTranslatorService):

    # You need to require a private api key if you want to use the yandex translator      

    def __init__(self):

        self.developer_key = getattr(settings, 'YANDEX_TRANSLATE_KEY', None)
        assert self.developer_key, ('`YANDEX_TRANSLATE_KEY` is not configured, '
                                    'it is required by `YandexTranslatorService. '
                                    'You need to require a private api key if you want to use the yandex translator. Visit the official website for more information about how to get one')

    def translate_string(self, text, target_language, source_language='en'):
        self.service = YandexTranslator(
            self.developer_key,
        )
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(source=source_language, 
            target=target_language, text=text)
    
class MicrosoftTranslatorService(BaseTranslatorService):

    """
    You need to require an api key if you want to use the microsoft translator. 
    Visit the official website for more information about how to get one. Microsoft offers a free tier 0 subscription (2 million characters per month).
    """

    def __init__(self):

        self.developer_key = getattr(settings, 'MICROSOFT_TRANSLATE_KEY', None)
        assert self.developer_key, ('`MICROSOFT_TRANSLATE_KEY` is not configured, '
                                    'it is required by `MicrosoftTranslatorService. '
                                    'You need to require an api key if you want to use the microsoft translator. Visit the official website for more' 
                                    ' information about how to get one. Microsoft offers a free tier 0 subscription (2 million characters per month).')

    def translate_string(self, text, target_language):
        self.service = MicrosoftTranslator(
            target=target_language, 
            api_key=self.developer_key,
        )
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text=text)
    

class PapagoTranslatorService(BaseTranslatorService):
    """
    You need to require an api key if you want to use the microsoft translator. 
    Visit the official website for more information about how to get one. Microsoft offers a free tier 0 subscription (2 million characters per month).
    """

    def __init__(self):

        self.client_id = getattr(settings, 'PAPAGO_CLIENT_ID', None)
        assert self.secret_key, ('`PAPAGO_CLIENT_ID` is not configured, '
                                    'it is required by `PapagoTranslatorService. '
                                    'You need to require a client id if you want to use the papago translator.'
                                    'Visit the official website for more information about how to get one.')

        self.secret_key = getattr(settings, 'PAPAGO_SECRET_KEY', None)
        assert self.secret_key, ('`PAPAGO_SECRET_KEY` is not configured, '
                                    'it is required by `PapagoTranslatorService. '
                                    'You need to require a client id if you want to use the papago translator.'
                                    'Visit the official website for more information about how to get one.')


    def translate_string(self, text, target_language, source_language="en"):
        self.service = PapagoTranslator(
            target=target_language, 
            source=source_language,
            client_id=self.client_id,
            secret_key=self.secret_key,
        )
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text=text)
    

class LibreTranslatorService(BaseTranslatorService):
    """
    Libre translate has multiple mirrors which can be used for the API endpoint. 
    Some require an API key to be used. By default the base url is set to libretranslate.de . 
    This can be set using the “base_url” input parameter.
    """

    def translate_string(self, text, target_language, source_language="en", ):
        self.service = LibreTranslator(
            target=target_language, 
            source=source_language,
            base_url=getattr(settings, 'LIBRE_TRANSLATE_MIRROR_URL', 'https://libretranslate.com/'), 
            client_id=self.client_id,
            api_key=getattr(settings, 'LIBRE_TRANSLATE_KEY', None)
        )
        
        assert isinstance(text, six.string_types), '`text` should a string literal'
        return self.service.translate(text=text)
    


