import logging
import os
from optparse import make_option

import polib
from django.conf import settings
from django.core.management.base import BaseCommand

from django_deep_translator.utils import get_translator

logger = logging.getLogger(__name__)

default_options = () if not hasattr(BaseCommand, 'option_list') \
    else BaseCommand.option_list


class Command(BaseCommand):
    help = ('autotranslate all the message files that have been generated '
            'using the `makemessages` command.')

    option_list = default_options + (
        make_option('--locale', '-l', default=[], dest='locale', action='append',
                    help='autotranslate the message files for the given locale(s) (e.g. pt_BR). '
                         'can be used multiple times.'),
        make_option('--untranslated', '-u', default=False, dest='skip_translated', action='store_true',
                    help='autotranslate the fuzzy and empty messages only.'),
        make_option('--set-fuzzy', '-f', default=False, dest='set_fuzzy', action='store_true',
                    help='set the fuzzy flag on autotranslated messages.'),
        make_option('--source-language', '-s', default='en', dest='source_language', action='store',
                    help='override the default source language (en) used for translation.'),
    )

    def add_arguments(self, parser):
        # Previously, only the standard optparse library was supported and
        # you would have to extend the command option_list variable with optparse.make_option().
        # See: https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/#accepting-optional-arguments
        # In django 1.8, these custom options can be added in the add_arguments()
        parser.add_argument('--locale', '-l', default=[], dest='locale', action='append',
                            help='autotranslate the message files for the given locale(s) (e.g. pt_BR). '
                                 'can be used multiple times.')
        parser.add_argument('--untranslated', '-u', default=False, dest='skip_translated', action='store_true',
                            help='autotranslate the fuzzy and empty messages only.')
        parser.add_argument('--set-fuzzy', '-f', default=False, dest='set_fuzzy', action='store_true',
                            help='set the fuzzy flag on autotranslated messages.')
        parser.add_argument('--source-language', '-s', default='en', dest='source_language', action='store',
                            help='override the default source language (en) used for translation.')

    def set_options(self, **options):
        self.locale = options['locale']
        self.skip_translated = options['skip_translated']
        self.set_fuzzy = options['set_fuzzy']
        self.source_language = options['source_language']

    def handle(self, *args, **options):
        self.set_options(**options)

        assert getattr(settings, 'USE_I18N', False), 'i18n framework is disabled'
        assert getattr(settings, 'LOCALE_PATHS', []), 'locale paths is not configured properly'
        for directory in settings.LOCALE_PATHS:
            # walk through all the paths and find all the pot files
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if not file.endswith('.po'):
                        # process file only if it is a .po file
                        continue

                    # get the target language from the parent folder name
                    target_language = os.path.basename(os.path.dirname(root))

                    if self.locale and target_language not in self.locale:
                        logger.info('skipping translation for locale `{}`'.format(target_language))
                        continue

                    self.translate_file(root, file, target_language)

    def translate_file(self, root, file_name, target_language):
        """
        convenience method for translating a po file

        :param root:            the absolute path of folder where the file is present
        :param file_name:       name of the file to be translated (it should be a pot file)
        :param target_language: language in which the file needs to be translated
        """
        logger.info('filling up translations for locale `{}`'.format(target_language))

        po = polib.pofile(os.path.join(root, file_name))
        for entry in po:
            # skip translated
            if self.skip_translated and entry.translated():
                continue

            translation = get_translator()
            entry.msgstr = translation.translate_string(text=entry.msgid, source_language=self.source_language,
                                                        target_language=target_language)
            if self.set_fuzzy:
                entry.flags.append('fuzzy')

        po.save()
