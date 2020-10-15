#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    author : Jean-Damien Généro
    date : 10 octobre 2020
    python pwb.py diplomates.py
"""

# IMPORTS
import datetime
import locale
import re
import requests
import pywikibot


# REQUEST FOR THE JSON
r = requests.get("https://jorfsearch.steinertriples.fr/tag/ambassadeur_pays?format=JSON")
j = r.json()


# PYWIKIBOT CONFIGURATION
site = pywikibot.Site()
page = pywikibot.Page(site, "Utilisateur:Ath wik/Brouillon")


# SETTING LOCALE TIME
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


# SETTING EMPTY DICTS AND LISTS
ambassades = {}
diplodict = {}
wrong = {}
good = []


# SETTING DICTS AND LIST
# JSON forms : WP forms
corrects_forms = {"Arabie Saoudite": "Arabie saoudite", "République algérienne démocratique populaire": "Algérie",
                  "République démocratique fédérale d'Ethiopie": "Éthiopie", "Îles Salomon": "Salomon",
                  "Vietnam": "Viêt Nam", "Etats-Unis": "États-Unis", "Somalie": "Somalie",
                  "Afrique du sud": "Afrique du Sud", "Jamaique": "Jamaïque"}

# special ref for non-resident ambassadors
non_resident = {"Afrique du Sud": "<ref group=n>Également ambassadeur auprès du [[Lesotho]].</ref>",
                "Fidji": "<ref group=n>Également ambassadeur auprès de [[Nauru]], des [[Tuvalu]], des [[Kiribati]] et "
                         "des [[Tonga]].</ref>",
                "Gabon": "<ref group=n>Également ambassadeur auprès de [[Sao Tomé-et-Principe]].</ref>",
                "Guinée": "<ref group=n>Également ambassadeur auprès du [[Sierra Leone]].</ref>",
                "Indonésie": "<ref group=n>Également ambassadeur auprès du [[Timor oriental]].</ref>",
                "Italie": "<ref group=n>Également ambassadeur auprès de [[Saint-Marin]].</ref>",
                "Mozambique": "<ref group=n>Également ambassadeur auprès du [[Swaziland]].</ref>",
                "Nouvelle-Zélande": "<ref group=n>Également ambassadeur auprès des [[îles Cook]] et des [[îles "
                                    "Samoa]].</ref>",
                "Panama": "<ref group=n>Également ambassadeurs auprès des [[Bahamas]].</ref>",
                "Papouasie-Nouvelle-Guinée": "<ref group=n>Également ambassadeur auprès des [[îles Salomon]].</ref>",
                "Philippines": "<ref group=n>Également ambassadeur auprès des [[îles Marshall]], de la [[États "
                               "fédérés de Micronésie|Micronésie]] et des [[Palaos]].</ref>",
                "Sainte-Lucie": "<ref group=n>Également ambassadeur auprès d'[[Antigua-et-Barbuda]], de la [["
                                "Barbade]], de la [[Dominique (pays)|Dominique]], de la [[Grenade (pays)|Grenade]], "
                                "de [[Saint-Christophe-et-Niévès]] et de [[Saint-Vincent-et-les-Grenadines]].</ref>",
                "Salvador": "<ref group=n>Également ambassadeur auprès du [[Belize]].</ref>",
                "Sénégal": "<ref group=n>Également ambassadeur auprès de la [[Gambie]].</ref>",
                "Sri Lanka": "<ref group=n>Également ambassadeur auprès des [[Maldives]].</ref>",
                "Suisse": "<ref group=n>Également ambassadeur auprès du [[Liechtenstein]].</ref>",
                "Suriname": "<ref group=n>Également ambassadeur auprès du [[Guyana]].</ref>",
                "Trinité-et-Tobago": "<ref group=n>Également ambassadeur auprès de la [[Barbade]].</ref>",
                "Zimbabwe": "<ref group=n>Également ambassadeur auprès du [[Malawi]].</ref>"}

# lines that will not be changed
no_modif = ["Russie", "Laos", "États-Unis", "Cameroun"]

# GETTING INFOS FROM THE JSON
for item in j:
    pays = item["ambassadeur_pays"]
    if pays not in ambassades.keys():
        ambassades[pays] = ["{} {}".format(item["prenom"], item["nom"]),
                            item["source_date"],
                            item["source_id"]]
# print(ambassades)


# MAKING A DICT where "Country" = ["ambassador", "date", "ref JORFTEXT\d+"]
for key, value in ambassades.items():
    year = re.sub(r'(\d{4})-\d{2}-\d{2}', '\\1', value[1])
    if int(year) > 2013:
        # print("{} : {}".format(key, value))
        if key in corrects_forms.keys():
           key = corrects_forms[key]
           diplodict[key] = value
        else:
            diplodict[key] = value
# print(diplodict)


"""
# CHECKING IF ALL THE COUNTRIES ARE IN THE WP PAGE
for country in diplodict:
    if country in page.text:
        print("------> {}".format(country))
    else:
        print("--//--> {}".format(country))
        # countries with // need to be added to corrects_forms."""


# MAKING A LIST OF COUNTRY FOR WHOM CHANGE IS NEEDED
for country in diplodict:
    url = "https://www.legifrance.gouv.fr/jorf/id/{}".format(diplodict[country][2])
    decree = requests.get(url)
    try:
        title = re.findall(r'(Décret du \d{1,2} [\wéèû]+ \d{4})', decree.text)
        ref = "<ref>{{{{Légifrance|base=JORF|url={} |texte={}}}}}.</ref>".format(url, title[0])
    except IndexError:
        title = "Décret de nomination de " + diplodict[country][0]
        ref = "<ref>{{{{Légifrance|base=JORF|url={} |texte={}}}}}.</ref>".format(url, title)
        title_date = "UNFOUND fo {}".format(country)
        continue
    title = re.findall(r'(Décret du (\d{1,2} [\wéèû]+ \d{4}))', decree.text)
    # print(title[0])  # ('Décret du 10 septembre 2020', '10 septembre 2020')
    ref = "<ref>{{{{Légifrance|base=JORF|url={} |texte={}}}}}.</ref>".format(url, title[0][0])
    title_date = datetime.datetime.strptime(str(title[1][1]), '%d %B %Y')
    decreedate = title_date.strftime('%d|%B|%Y').lstrip("0").replace(" 0", " ")
    # print(decreedate)  # 10|septembre|2020
    nomination_date4 = "{{{{tri date|{}}}}}".format(decreedate)
    # print(nomination_date4)  # {{tri date|10|septembre|2020}}
    if nomination_date4 not in page.text and country not in no_modif:
        # print("--//--> {} ({} : {})".format(country, title[0], url))
        wrong[country] = [nomination_date4, ref]


# CHANGING WP PAGE TEXT
for item in wrong:
    # print(diplodict[item])
    new_ambassador = diplodict[item][0]
    if item in non_resident:
        pattern0 = r'(\| {{' + item + '}} ?\|{2} ?\[{2}Am.+\]{2} ?\|{2} ?)[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref group=n>.+<\/ref>)? ?\|{2} ?align="right" ?\| ?){{t?T?ri ?date\|\d{1,2}\|.+\|\d{4}}}( {0,}\|{1,2} {0,})(<ref>.+\n?<\/ref>)?({{,}}<ref>.+\n?<\/ref>)?'
        page.text = re.sub(pattern0,
                           "\\1[[{}]]{}\\2{}\\3 || {}".format(diplodict[item][0], non_resident[item], wrong[item][0], wrong[item][1]),
                           page.text)
    else:
        pattern0 = r'(\| {{' + item + '}} ?\|{2} ?\[{2}Am.+\]{2} ?\|{2} ?)[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref group=n>.+<\/ref>)? ?\|{2} ?align="right" ?\| ?){{t?T?ri ?date\|\d{1,2}\|.+\|\d{4}}}( {0,}\|{1,2} {0,})(<ref>.+\n?<\/ref>)?({{,}}<ref>.+\n?<\/ref>)?'
        page.text = re.sub(pattern0,
                           "\\1[[{}]]\\2{}\\3 || {}".format(diplodict[item][0], wrong[item][0], wrong[item][1]),
                           page.text)
print(page.text)

# SAVING PAGE
# page.save("mise à jour : " + ', '.join(wrong))
