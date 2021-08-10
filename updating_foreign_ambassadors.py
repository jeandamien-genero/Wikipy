#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    author : Jean-Damien Généro
    date : 2020-10-09
    update : 2021-08-10
    python pwb.py amb_etran.py
"""

import re
import pywikibot
import datetime
import locale


locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

def f_ambassadors(txt):
    """
    Extracting from JORF "Remise des lettres de créances" new ambassadors' names and countries.
    :param txt: path to a document .txt with JORF text "Remise des lettres de créances"
    :type txt: str
    :return: list of ambassadors names + countries
    :rtype: list
    """
    with open(txt, 'r', encoding='utf-8') as opening:
        file = opening.read()
        search = re.findall(r"Son Excellence Mm?e?\.? (.+), qui lui a remis les lettres l'accréditant en qualité d'ambassad(eur|rice) extraordinaire et plénipotentiaire d[eu]( l[ae])? (.+) ?[;\.]+", file)
    new_ambassadors = []
    correct_forms = {"Algérienne": "Algérie", "Gabonaise": "Gabon", "Tunisienne": "Tunisie", "Equateur": "Équateur",
                     "Elsalvador": "Salvador", "Egypte": "Égypte", "Arabiesaoudite": "Arabie saoudite",
                     "Corée": "Corée du Sud", "Srilanka": "Sri Lanka"}
    for item in search:
        country = re.sub(r"(République|Royaume).+(de|du|d') ?", "", str(item[3]))
        unecessaries = ["République ", " démocratique et populaire ", "Confédération "]
        for unnecessary in unecessaries:
            country = country.replace(unnecessary, "")
        if country[-1] == " ":
            country = country.replace(country[-1], "")
        country = country.title()
        for correct in correct_forms:
            if correct == country:
                country = country.replace(country, correct_forms[correct])
        new_ambassadors.append([item[0], country])
    # print(new_ambassadors)
    return new_ambassadors


def updating_page(date, jorf_id) -> None:
    """
    Updating wp:fr page "Liste des actuels ambassadeurs étrangers en France"
    :param date: ceremony's date = dd|mm|yyyy
    :type date: str
    :param jorf_id: jorf text ID (JORFTEXT000043359775)
    :type jorf_id: str
    :return: none
    """
    # PYWIKIBOT CONFIGURATION
    site = pywikibot.Site()
    page = pywikibot.Page(site, "Liste des actuels ambassadeurs étrangers en France")
    # 1/ MAKING DATE
    full_date = datetime.datetime.strptime(date, '%d|%m|%Y')
    num_date = '{:%d|%m|%Y}'.format(full_date)  # dd|mm|yyyy
    ref_date = '{:%d%m%Y}'.format(full_date)  # ddmmyyyy
    alpha_date = '{:%d %B %Y}'.format(full_date)  # dd month yyyy
    # 2/ MAKING REF
    url = "https://www.legifrance.gouv.fr/jorf/id/" + jorf_id
    ref_title = "Remise de lettres de créance du " + alpha_date
    ref_name = '<ref name ="ldc{}" />'.format(ref_date)
    ref_txt = '<ref name ="ldc{}">{{{{Légifrance|base=JORF|url={}|texte={}}}}}.</ref>'.format(ref_date, url, ref_title)
    page.text = page.text.replace("lettres de créance du 10 décembre 2019}}.</ref>",
                                  "lettres de créance du 10 décembre 2019}}.</ref>\n" + ref_txt)
    # 3/ NOMINATIONS LIST
    nominations = f_ambassadors(<JORF txt>)
    # 4/ UPDATING
    maj = []
    for nomination in nominations:
        pattern = "| {{" + nomination[1] + "}}\n| [[Ambassade d"
        line = '(\| {{' + str(nomination[1]) + '}}\n\| \[\[Am.+\]\]\n\| \[\[).+(\]\]\n\| align="right" \| {{tri date)\|\d+\|[0-9a-zéèû]+\|\d+(}} \|\| ).+'
        if pattern in page.text:
            maj.append(nomination[1])
            page.text = re.sub(line, "\\1" + nomination[0].title() + "\\2|" + num_date + "\\3" + ref_name, page.text)
    # updating the update date at the top of the page
    page.text = re.sub(r"La liste qui suit a été mise à jour après la cérémonie de remise de lettres de créance du \d+ [\wéèû]+ \d+",
                       "La liste qui suit a été mise à jour après la cérémonie de remise de lettres de créance du " + alpha_date, page.text)
    maj_list = "mise à jour automatique : {}".format(", ".join(maj))
    page.save(maj_list)
    print(maj_list)
