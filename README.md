# django-deep-translator 
[![Upload Python Package](https://github.com/wmo-raf/django-deep-translator/actions/workflows/publish.yml/badge.svg)](https://github.com/wmo-raf/django-deep-translator/actions/workflows/publish.yml)

Autotranslate django `.po` translation files package built on top of  [deep-translator](https://pypi.org/project/deep-translator/)

## Installation

```bash
pip install django-deep-translator
```

Add `'django_deep_translator'` to your `INSTALLED_APPS` setting:

```py
INSTALLED_APPS = (
        ...
        'django_deep_translator',
    )

```

## Quickstart

```bash 
python manage.py translate_messages
```

The command finds all the generated pot (.po) files under the locale paths (LOCALE_PATHS) specified in django project settings, and translates them automatically with default source language as **english**.

## Options

- ``-f, --set-fuzzy``: Set the 'fuzzy' flag on autotranslated entries
- ``-l, --locale 'locale'``: Only translate the specified locales
- ``-u, --untranslated``: Only translate the untranslated messages
- ``-s, --source-language``: Override the default source language (en) used for translation

```bash
    python manage.py translate_messages -l 'de' -l 'es'
```

## Settings

In your settings, list the relative path to locale folders, example:

```py
LOCALE_PATHS = (
    'locale',
    'home/locale',
    'products/locale',
    'services/locale',
)
```

---

Using a different Translation Service:

```python
    # default: 'django_deep_translator.services.GoogleTranslatorService'
    PO_TRANSLATOR_SERVICE = 'django_deep_translator.services.GoogleAPITranslatorService'
```

---


`PO_TRANSLATOR_SERVICE` accepts the following services with respective additional variables:

| Service                        | Additional variables      | Description |
| :---------------------------  | :--------------------    | :---------- |
| **GoogleAPITranslatorService**     |    -          | - |
| **MicrosoftTranslatorService**     | `MICROSOFT_TRANSLATE_KEY` | You need to require an api key if you want to use the microsoft translator. Visit the official website for more information about how to get one. Microsoft offers a free tier 0 subscription (2 million characters per month). |
| **PonsTranslatorService**          | - | - |
| **MyMemoryTranslatorService**      | - | - |
| **YandexTranslatorService**        | `YANDEX_TRANSLATE_KEY` | You need to require a private api key if you want to use the yandex translator. Visit the official website for more information about how to get one |
| **PapagoTranslatorService**        | `PAPAGO_CLIENT_ID`, `PAPAGO_SECRET_KEY`| You need to require a client id if you want to use the papago translator. Visit the official website for more information about how to get one. |
| **DeeplTranslatorService**         | `DEEPL_TRANSLATE_KEY` | Visit https://www.deepl.com/en/docs-api/ for more information on how to generate your Deepl api key |
| **QcriTranslatorService**          | `QCRI_TRANSLATE_KEY` | Visit https://mt.qcri.org/api/ for more information |
| **LibreTranslatorservice**         | `LIBRE_TRANSLATE_MIRROR_URL` | Libre translate has multiple mirrors which can be used for the API endpoint. Some require an API key to be used. By default the base url is set to libretranslate.de . |

