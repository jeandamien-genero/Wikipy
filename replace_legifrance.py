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
    date : 23 mai 2020
"""

# 1. Imports
import re
import requests
from bs4 import BeautifulSoup
import pywikibot


# 2. Functions
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


def fill_lgf_template(article, patterns_dict):
    """Replaces any refs that links to the website of official french laws and decrees
       (www.legifrance.gouv.fr.) by the structured template {{Légifrance}} (french wikipedia).
    :param article: a wikipedia parge parsed by pywikibot.
    :type article: pywikibot.page.Page
    :param patterns_dict: a dictionary containing patterns of the old refs as its keys (str)
                          and the position of the url's captured group as its values (int).
    :type patterns_dict: dict
    :return: a dict with the old refs as keys and the new as values.
    :rtype: dict
    """
    dict_ref = {}
    for pattern in patterns_dict:
        search = re.findall(pattern, article.text)
        for item in search:
            r_search = requests.get(
                item[patterns_dict[pattern]])
            soup = BeautifulSoup(r_search.text, 'html.parser')
            title = soup.html.head.title.text
            title_pattern = '((Décret)?(Arrêté)? du \d? \w+ \d{4} [\w éèêôîûùïë\',\(\)\-\.]+)'
            title_search = re.search(title_pattern, title)
            nor_pattern = 'I?P?D?A?F?[A-Z]{3}[0-9]{7}[A-Z]'
            nor = re.findall(nor_pattern, r_search.text)
            if nor:
                model = '<ref{}>{{{{Légifrance|base=JORF|numéro={}|texte={}}}}}.</ref>'.format(
                    item[1], nor[0], title_search.group(1))
                dict_ref[item[0]] = model
    return dict_ref


# 3. Settings

dict_search = {
    '(<ref( name=\\"promo_[a-z]+\\")?>{{Article \|titre= ?((Décret)?(Arrêté)? du [1-9]\d? [a-zé]+ '
    '\d{4}[a-z \'éêè,{}0-9A-Zà\(\)-]+) ? ?\|périodique=Journal officiel de la République française'
    ' ?\|(lien périodique=Journal officiel de la République française ?\|)?numéro=\d+ \|jour=[1-9]'
    '\d? ?\|mois=[a-zé]+ ?\|année=\d{4} ?\|lire en ligne=(http(s)?:\/\/www\.legifrance\.gouv\.fr\/'
    'affichTexte\.do\?cidTexte=JORFTEXT\d+)([&categorieLien=id]+)?( )?}}\.<\/ref>)' : 6,

    '(<ref( name=\\"[a-zéA-Z_0-9 ]+\\")?>{{lien web\|titre=((Décret)?(Arrêté)? du ({{)?[1-9]\d?(er)?'
    '(}})? [a-zé]+ \d{4}[a-z \'éèê,{}0-9A-Zà\(\)-\|]+) ?\|site=(http(s)?:\/\/www\.)?legifrance.gouv.'
    'fr\/? ?\|périodique=\[?\[Journal.+\]\]?(, {{numé\w+\|\d+}})? ?\|((issn=\d+-\d+\|())?)(date=[1-9]'
    '\d? [a-zé]+ [0-9]{4}\|())?(issn=\d+-\d+\|()?)(date=[1-9]\d? [a-zé]+ [0-9]{4}\|())?(lire en ligne'
    ')?(url)?=(https:\/\/www\.legifrance\.gouv\.fr\/affichTexte\.do\?cidTexte=JORFTEXT[0-9]+)(&date'
    'Texte=)?(&categorieLien=id)? ?}}\.?<\/ref>)' : 22,

    '(<ref( name=\\"[a-zéA-Z_0-9 ]+\\")?>{{lien web\|url=(http(s)?:\/\/www\.legifrance\.gouv\.fr\/'
    'affichTexte\.do\?cidTexte=JORFTEXT\d+)(&dateTexte=)?(&categorieLien=id)?\|titre=((Décret)?'
    '(Arrêté)? du ({{)?[1-9]\d?(er)?(}})? [a-zé]+ \d{4}[a-z \'éèê,{}0-9A-Zà\(\)-\|]+) ?\|date=[1-9]'
    '\d? [a-zé]+ \d{4}\|site=(http(s)?:\/\/www\.)?legifrance\.gouv\.fr\/? ?\|(périodique)?(éditeur)?'
    '=\[?\[Journal.+\]\]?(, {{numé\w+\|\d+}})? ?\|(issn=\d+-\d+\|)?consulté le=\d{2} [a-z]+ \d{4}}}'
    '\.<\/ref>)' : 2,

    '(<ref( name=\\"[a-zéûA-Z_0-9 ]+\\")?>\[(http(s)?:\/\/www\.legifrance\.gouv\.fr\/affichTexte\.do'
    '([\w\-&%=\?\.;,! ]+)?)\s[A-Z].+\]\.?.+?\.?<\/ref>)' : 2,

    '(<ref( name=\\"[a-zéA-Z_0-9 ]+\\")?>{{\w+ ?(\w+)?\|titre=(Décret)?(Arrêté)? du ({{)?[1-9]\d?(er)?'
    '(}})? [a-zé]+ \d{4}[a-z \'éè,{}0-9A-Zà\(\)-\|]+ ?\|lire en ligne=(((http(s)?:\/\/www\.legifrance'
    '\.gouv\.fr\/affichTexte\.do\?cidTexte=JORFTEXT\d+)(&dateTexte=)?(&categorieLien=id)?)) ?\|consulté'
    'le=(\d{2} [a-z]+ \d{4})?(\d{4}-\d{2}-\d{2})?(\d{2}-\d{2}-\d{4})?}}<\/ref>)' : 10,

    '(<ref( name=\\"promo_[a-z]+\\")?>\[?(http(s)?:\/\/www\.legifrance\.gouv\.fr\/affichTexte\.do([\w\-&'
    '%=\?\.;,! ]+)?)\]?<\/ref>)' : 2
}

site = pywikibot.Site()
page = pywikibot.Page(site, u"__page that will be modify___")


# 4. Writing the changes in the wp page by applying the fill_lgf_template function :
page.text = replace_all(page.text, fill_lgf_template(page, dict_search))
page.save(u"bot : intégration du modèle Légifrance dans les références pointant vers le JORF")
