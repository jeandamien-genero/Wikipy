#!/usr/bin/python
# -*- coding: UTF-8 -*-


"""
author : Jean-Damien Généro
Date : 2020-10-08
Update : 2021-08-07
Updating wp:fr's list of current french ambassadors
python3 pwb.py ambassadors2021.py
"""

import re
import pywikibot
import requests
import sys
import datetime
import locale


locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


# json_url = sys.argv[1]


def ambassadors(json_url):
    """
    parsing a JSON with all ambassadors nominations and making a list with only the last ones
    :param json_url: URL to a JSON with nomination
           (https://jorfsearch.steinertriples.fr/tag/ambassadeur_pays?format=JSON)
    :type json_url: str
    :return: a list with all last nominations by country
           ['ambassador', 'JORF date', 'country', 'JORF text id', 'Jorf date - one day', 'nomination year']
           >> ['Elisabeth Barsacq', '2020-10-02', 'Albanie', 'JORFTEXT000042387663', '01-octobre-2020', '2020']
    :rtype: list
    """
    r = requests.get(json_url)
    j = r.json()
    # 1/ MAKING LISTS WITH ambassadors + countries
    ambassadeurs = []
    all_countries = []
    # dict with JORF forms: WP forms
    forms = {"République dominicaine": "Dominique", "Arabie saoudite": "Arabie Saoudite", "États-Unis": "Etats-Unis",
             "Fidji": "Fidji", "Guatemala": "République du Guatémala", "Israël": "Israël", "Japon": "Japon",
             "Jordanie": "Jordanie", "Laos": "Laos", "République de Macédoine": "Macédoine", "Rwanda": "Rwanda",
             "Turquie": "Turquie", "Viêt Nam": "Vietnam"}
    for item in j:
        if item["type_ordre"] == "nomination":
            individual = item["prenom"] + " " + item["nom"]
            d = datetime.datetime.strptime(item["source_date"], '%Y-%m-%d')
            date = '{:%Y-%m-%d}'.format(d)
            country = item["ambassadeur_pays"]
            for wrong in forms:
                if country == forms[wrong]:
                    country = country.replace(forms[wrong], wrong)
            all_countries.append(country)
            txt = item["source_id"]
            ambassadeurs.append([individual, date, country, txt])
    countries = set(all_countries)
    # 2/ MAKING A DICT WITH "country": [ambassadors]
    insittutions = {}
    for country in countries:
        insittutions[country] = []
    for item in ambassadeurs:
        insittutions[item[2]].append(item)
    # 3/ SEARCHING LAST NOMINATION
    last_nomintions = []
    for country_name in insittutions:
        time = []
        for individual_infos in insittutions[country_name]:
            # making a list with date only in order to pick the most recent one
            time.append(individual_infos[1])
        jo_date = datetime.datetime.strptime(max(time), '%Y-%m-%d')
        for individual_infos in insittutions[country_name]:
            if '{:%Y-%m-%d}'.format(jo_date) in individual_infos[1]:
                # decree date = jorf date - 1 day
                old_decree = jo_date - datetime.timedelta(days=1)
                decree = '{:%d-%B-%Y}'.format(old_decree)
                year = '{:%Y}'.format(old_decree)
                individual_infos.append(decree)
                individual_infos.append(year)
                last_nomintions.append(individual_infos)
    return last_nomintions


def updating_ambassadors(article, unwanted_changes) -> None:
    site = pywikibot.Site()
    page = pywikibot.Page(site, article)
    MAJ = []
    for nomination in ambassadors("https://jorfsearch.steinertriples.fr/tag/ambassadeur_pays?format=JSON"):
        # nomination[2] = country
        if nomination[2] not in unwanted_changes:
            # nomination[5] = nomination year
            if nomination[5] == '2020' or nomination[5] == "2021":
                # nomination[3] = JORF text id
                if nomination[3] not in page.text:
                    # search = country (nomination[2])'s line in page.text
                    search = re.findall('(\| +\{\{' + nomination[2] + '\}\} +\|\|.+\|\|.+\|\| align=\"right\" \| ?{{[tT]ri date\|\d+\|[éèûa-zA-Z0-9]+\|\d+)', page.text)
                    try:
                        search[0]
                    except IndexError:
                        continue
                    new_year = search[0] + nomination[5]  # country'line + new year
                    if new_year not in page.text:
                        new_year = re.sub(r"[tT]ri +date.+", "tri date|" + nomination[4].replace('-', '|'), new_year)
                        new_year = new_year + "}} || <ref>{{Légifrance|base=JORF|url=https://www.legifrance.gouv.fr/jorf/id/"+ nomination[3] + "|texte=Décret du " + nomination[4].replace('-', ' ') + "}}.</ref>"
                        page.text = page.text.replace(search[0], new_year)
                        page.text = re.sub(r'(\| +\{\{' + nomination[2] + '\}\} +\|\|.+\|\|).+(\|\| align=\"right\")',
                                           "\\1[[" + nomination[0] + "]]\\2", page.text)
                        page.text = re.sub(r"</ref>}}.+(\n</ref>)?", "</ref>", page.text)
                        # adding country name to the MAJ list for the commit message
                        MAJ.append(nomination[2])
    # updating the update date at the top of the page
    today = datetime.date.today()
    thisday = today.strftime("%d %B %Y")
    page.text = re.sub(r"La liste qui suit a été mise à jour le \d+ [\wéèû]+ \d+", "La liste qui suit a été mise à jour le " + thisday, page.text)
    # deal with exep here if needed
    # print(page.text)
    page.save("mise à jour automatique : {}".format(", ".join(sorted(MAJ))))
    print("DONE")


no_need = ["Arabie saoudite", "Australie", "Biélorussie", "Bosnie-Herzégovine", "Brésil", "Colombie", "Finlande",
           "Kazakhstan", "Lettonie", "Paraguay", "Russie"]
