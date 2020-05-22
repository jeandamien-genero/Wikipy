#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
    Script that replaces the cite journal template by the legifrance template when links
    to the website of official french laws and decrees (www.legifrance.gouv.fr.).
    
    Exemples : 
    
    <ref name="promo">
        {{Article |titre=Décret du XX month XXXX \\w |périodique=Journal officiel de la
        République française |numéro=\\d\\d |jour=\\d\\d |mois=month |année=\\d\\d\\d\\d
        |lire en ligne=https://www.legifrance.gouv.fr/\\w+}}.
    </ref>

    will be replaced by

    <ref name="promo">
        {{Légifrance|base=JORF|numéro=\\w+|texte=Décret du XX month XXXX \\w}}.
    </ref>

    author : Jean-Damien Généro
    date : 22 mai 2020
"""

import re
import requests
from bs4 import BeautifulSoup
import pywikibot


def replace_all(article, dic):
    """"Replaces in a text a dict key by its value.
    :param article: a wp page
    :type article: str
    :param dic: a dict
    :type dic: dict
    :return: str
    """
    for key, value in dic.items():
        article = article.replace(key, value)
    return article

# 1. Settings
site = pywikibot.Site()
page = pywikibot.Page(site, u"__page that will be modify___")
dict_ref = {}

# 2. Pattern
legifrance = '(<ref( name=\\"[a-z_]+\\")?>{{Article \\|titre= ?((Décret)?(Arrêté)? du [1-9]\
              [0-9]? [a-zé]+ [0-9]{4}[a-z \'é,{}0-9A-Zà\\(\\)-]+) ?\\|périodique=Journal officiel\
               de la République française ?\\|(lien périodique=Journal officiel de la République \
               française ?\\|)?numéro=[0-9]+ \\|jour=[1-9][0-9]? ?\\|mois=[a-zé]+ ?\\|année=[0-9]\
               {4} ?\\|lire en ligne=(https:\\/\\/www\\.legifrance\\.gouv\\.fr\\/affichTexte\\.do\
               \\?cidTexte=JORFTEXT[0-9]+)([&categorieLien=id]+)?( )?}}\\.<\\/ref>)'
"""
                                    ======= Captured groups =======
                | 0. all | 1. @name in <ref> | 2. decree's title | 3. str 'Décret' |
                | 4. str 'Arrêté' | 5. blank | 6. decree url | 7. blank | 8. blank |
"""

# 3. Searching for all regex occurrences in the wp page.
search = re.findall(legifrance, page.text)

# 4. Iterating on each result of the previous search
for item in search:
    # Making a request for the decree :
    r_legifrance = requests.get(item[6])
    # Making a soup with it :
    soup = BeautifulSoup(r_legifrance.text, 'html.parser')
    # Defining a pattern for the NOR number and searching for all its occurrences in the decree :
    nor_pattern = 'P?D?A?[A-Z]{3}[0-9]{7}[A-Z]'
    NOR = re.findall(nor_pattern, r_legifrance.text)
    # When a result is found, we make the legifrance template using it and the 1st regex's results :
    if NOR:
        model = '<ref{}>{{{{Légifrance|base=JORF|numéro={}|texte={}}}}}.</ref>'\
                .format(item[1], NOR[0], item[2])
        # adding to the dict the old journal template and the new legifrance template
        dict_ref[item[0]] = model

# 5. Writing the changes in the wp page by applying the replace_all function :
page.text = replace_all(page.text, dict_ref)
print(page.text)
page.save(u"bot : __modification message__")
