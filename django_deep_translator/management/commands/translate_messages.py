import logging
import os
from optparse import make_option

import polib
from tqdm.auto import tqdm
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

        locale_paths = list(settings.LOCALE_PATHS)
        logger.info(f"Found {len(locale_paths)} locale directory(ies). Starting translation...")

        # Outer progress bar: locales
        with tqdm(total=len(locale_paths), desc="Locales", unit="locale", colour="cyan", ncols=100) as locale_bar:
            for directory in locale_paths:
                self.process_locale_directory(directory)
                locale_bar.update(1)

    def process_locale_directory(self, directory):
        """Process all .po files inside a locale directory."""
        po_files_to_process = []
        for root, dirs, files in os.walk(directory):
            po_files = [f for f in files if f.endswith('.po')]
            for file in po_files:
                target_language = os.path.basename(os.path.dirname(root))
                if self.locale and target_language not in self.locale:
                    logger.info(f"Skipping locale `{target_language}` (not in selected locales).")
                    continue
                po_files_to_process.append((root, file, target_language))

        if not po_files_to_process:
            return

        # Inner progress bar for files
        with tqdm(total=len(po_files_to_process), desc=f"{os.path.basename(directory)} files", unit="file", colour="blue", ncols=100, leave=False) as file_bar:
            for root, file, target_language in po_files_to_process:
                self.translate_file(root, file, target_language)
                file_bar.update(1)

    def translate_file(self, root, file_name, target_language):
        """Translate all entries in a .po file with progress feedback."""
        file_path = os.path.join(root, file_name)
        po = polib.pofile(file_path)
        translator = get_translator()

        entries_to_translate = [
            e for e in po if not (self.skip_translated and e.translated())
        ]
        total = len(entries_to_translate)

        if total == 0:
            logger.info(f"No entries to translate for `{target_language}` in `{file_path}`.")
            return

        logger.info(f"Translating {total} entries for `{target_language}` ({file_path})...")

        # Deepest level progress bar for entries
        with tqdm(total=total, desc=f"→ {target_language}:{file_name}", unit="msg", colour="green", ncols=100, leave=False) as msg_bar:
            for entry in entries_to_translate:
                try:
                    entry.msgstr = translator.translate_string(
                        text=entry.msgid,
                        source_language=self.source_language,
                        target_language=target_language
                    )
                    if self.set_fuzzy:
                        entry.flags.append('fuzzy')
                    msg_bar.set_postfix({
                        "progress": f"{msg_bar.n + 1}/{total}",
                        "current": entry.msgid[:40] + ("..." if len(entry.msgid) > 40 else "")
                    })
                except Exception as e:
                    logger.error(f"Failed to translate '{entry.msgid}': {e}")
                    msg_bar.set_postfix_str("Error")
                finally:
                    msg_bar.update(1)

        po.save()
        logger.info(f"✅ Saved translated file: {file_path}")
