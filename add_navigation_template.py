#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
    author : Jean-Damien Généro
    date : 29 mai 2020
"""

import re
import pywikibot


def remove_red_links(red_lk_list, list_to_be_checked):
    """Removes red links from a list of wiki links.
    :param red_lk_list: a list of wiki red links
    :type red_lk_list: list
    :param list_to_be_checked: a list of wiki pages
    :type list_to_be_checked: list
    :return: list_to_be_checked
    :rtype: list
    """
    for link in red_lk_list:
        if link in list_to_be_checked:
            list_to_be_checked.remove(link)
    return list_to_be_checked


site = pywikibot.Site()
page = pywikibot.Page(site, "Modèle:Palette Chef d'état-major de la Marine (France)")

red_links = ['Eugène Sellier', 'Louis Victor Alquier', 'Charles Chauvin', 'Ernest Marquer',\
            'Paul Campion', 'Alfred Le Timbre', 'Alain Coatanéa', 'Jean-Charles Lefebvre']

pattern = '\\* \\[\\[([A-ZÉa-zéèïüç\'\\-]+ (de )?(Le )?(du )?(d\' )?[A-ZÉa-zéèïüç\\-\']+( \
        Émile Krantz)?( de)?( Lamornaix)?( Marie Le Bris)?( La Jaille)?( Dupetit-Thouars)?\
        ( Colstoun)?( Alquier)?( Ronarc\'h)?( Dainville)?( \\(amiral\\))?)\\|?'

search = re.findall(pattern, page.text)

pages_with_palette = []
pages_without_palette = []


for item in set(search):
    article = pywikibot.Page(site, item[0])
    already = '|Chef d\'état-major de la Marine (France)'
    if already not in article.text:
        if '{{Palette' not in article.text:
            pages_without_palette.append(item[0])
        elif '{{Palette' in article.text:
            pages_with_palette.append(item[0])


for item in remove_red_links(red_links, pages_with_palette):
    art_modif = pywikibot.Page(site, item)
    existing_tplt = re.search('({{Palette.+)(}})', art_modif.text)
    add_in_exst_tplt = existing_tplt.group(1) + '|Chef d\'état-major de la Marine (France)'\
                       + existing_tplt.group(2)
    art_modif.text = re.sub('{{Palette.+}}', add_in_exst_tplt, art_modif.text)
    art_modif.save("bot : + [[Modèle:Palette Chef d'état-major de la Marine (France)|Palette\
                    Chef d'état-major de la Marine (France)]]")

for item in remove_red_links(red_links, pages_without_palette):
    art_modif = pywikibot.Page(site, item)
    no_existing_tplt = re.search('{{Portail', art_modif.text)
    add_no_exst_tplt = '{{Palette|Chef d\'état-major de la Marine (France)}}\n\n{{Portail'
    art_modif.text = re.sub(no_existing_tplt.group(), add_no_exst_tplt, art_modif.text)
    art_modif.save("bot : + [[Modèle:Palette Chef d'état-major de la Marine (France)|Palette\
                    Chef d'état-major de la Marine (France)]]")
