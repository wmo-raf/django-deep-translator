import logging
import os
import time
from optparse import make_option
import string
import polib
import random 
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
        make_option('--silent', '-S', default=False, dest='silent', action='store_true',
                    help="Don't show the verbose output"),
        make_option('--throttle', '-t', default='10', dest='throttle_seconds', action='store_true',
                   help='Throttle the maximum seconds for the next translate request(default=10 sec)'),        
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
        parser.add_argument('--silent', '-S', default=False, dest='silent', action='store_true',
                            help="don't show the verbose output")
        parser.add_argument('--throttle', '-t', default='10', dest='throttle_seconds', action='store',
                            help='throttle the maximum of seconds for the next translate request(default=10 sec)')        
    def set_options(self, **options):
        self.locale = options['locale']
        self.skip_translated = options['skip_translated']
        self.set_fuzzy = options['set_fuzzy']
        self.source_language = options['source_language']
        self.silent = options['silent']
        self.throttle_seconds = int(options['throttle_seconds']) if options['throttle_seconds'].isdigit() else 1                

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

        if target_language in ['cn','zh_CN','zh_cn','zh-hans','zh-HAns','zh_HAns','zh_Hans','zh_hans']: 
            target_language = 'zh-CN'
            
        if target_language in ['he']: 
            target_language = 'iw'
            
        if target_language in ['nb']: 
            target_language = 'no'                        
            
        targets = self.count(po)
        count = 0
        translation = get_translator()
        source_language_name = self.get_language_name(self.source_language)
        target_language_name = self.get_language_name(target_language)         
        if source_language_name == '' or target_language_name == '':
            self.print("...source language {0} or target language {1} is not supported".format(self.source_language, target_language))
            return
        
        for entry in po:
            # skip translated
            if self.skip_translated and entry.translated():
                continue

            # skip if source text is not a text
            if self.source_language == 'en':
              if not self.is_text(entry.msgid):
                  continue            

            if self.throttle_seconds:              
              time.sleep(self.throttle_seconds)
            #print( dir(get_translator) )

            if entry.msgid_plural != "":
              if isinstance(entry.msgstr_plural, dict):
                if len(entry.msgstr_plural) == 2:
                  if entry.msgstr_plural[0] == '' or entry.msgstr_plural[1] == '':

                    self.print("{0}/{1}\t{2} => \t| {3}".format(count, targets, source_language_name, entry.msgid))                                  
                    entry.msgstr_plural[0] = translation.translate_string(text=entry.msgid, source_language=self.source_language, target_language=target_language)
                    self.print("\t{0}\t\t| {1}".format(target_language_name, entry.msgstr_plural[0]))

                    self.print("{0}/{1}\t{2} => \t| {3}".format(count, targets, source_language_name, entry.msgid_plural))
                    entry.msgstr_plural[1] = translation.translate_string(text=entry.msgid_plural, source_language=self.source_language, target_language=target_language)
                    self.print("\t{0}\t\t| {1}".format(target_language_name,entry.msgstr_plural[1]))
                    count += 1 
                    po.save()
            else: 
               if entry.msgstr == "":                                                              
                 self.print("{0}/{1}\t{2} -> \t| {3}".format(count, targets, source_language_name, entry.msgid))
                 entry.msgstr = translation.translate_string(text=entry.msgid, source_language=self.source_language, target_language=target_language)
                 self.print("\t{0} \t| {1}".format(target_language_name,entry.msgstr))
                 po.save()
                 count += 1                  
            if self.set_fuzzy:
                self.print("...flog to fuzzy")               
                entry.flags.append('fuzzy')


    def count(self, po):
      count = 1;
      for entry in po:
        if self.skip_translated and entry.translated():
          continue
        if self.source_language == 'en':
          if not self.is_text(entry.msgid):
            continue            

        if entry.msgid_plural != "":
          if isinstance(entry.msgstr_plural, dict):
            if len(entry.msgstr_plural) == 2:
              if entry.msgstr_plural[0] == '' or entry.msgstr_plural[1] == '':
                count += 1 
        else: 
          if entry.msgstr == "":                                                              
            count += 1
            
      return count 
                
    def is_text(self, s):
      for i in s:
        if i.upper() in string.ascii_uppercase:
          return True
      return False

    def print(self, msg):
      if self.silent == False:
        print(msg)

    def get_language_name(self, code):
      translation = get_translator()        
      supported_langs = translation.get_supported_languages()
      for i in supported_langs:
        if code == supported_langs[i]: 
          return i
      return ''
