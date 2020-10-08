#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    author : Jean-Damien Généro
    date : 9 octobre 2020
    using this decree = https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000042407440
"""

import re
import pywikibot

# INPUT DATA
decree = input("Path to the decree text ? ")
date = input("Date (|05|octobre|2020) ? ")
first_country = input("First country is alphabetical order ? ")
refname = input("Reference name (ldc...) ? ")
url = input("Url ? ")
decree_date = input("Decree date (make sure to add a blanck space at the begining) ? ")

# EMPTY LIST AND DICT
individuals = []
diplomats = {}

# PYWIKIBOT CONFIGURATION
site = pywikibot.Site()
page = pywikibot.Page(site, "Liste des actuels ambassadeurs étrangers en France")

# DICT AND LISTS
# countries' official names
country = {"Tchèque": "République tchèque", "Ivoire": "Côte d'Ivoire", "Panama": "Panamá"}
# countries which ambassade in France is located in Bruxelles :
Bruxelles_first = "Grenade" # first country with the full ref about Bruxelles
Bruxelles = ["Jamaïque", "Papouasi-Nouvelle-Guinée", "Salomon", "Trinité-et-Tobago", "Vanuatu"]
# countries which ambassade in France is located in London :
London_first = "Bahamas" # first country with the full ref about London
London = ["Guyana", "Maldives"]

# GETTING DIPLOMATS AND THEIR COUNTRY
with open(decree, "r") as file:
    for item in [line.strip() for line in file]:
        item = re.sub("Son Excellence Mm?e?\.? (.+),.+ l?d?'?([\wéèï]+) ?[,;]", "\\1 \\2", item)
        if "résidence" in item:
            item = re.sub("en résidence.+", "", item)
        individuals.append(item.title())

# MAKING A DICT WHERE COUNTRY = DIPLOMAT
for item in individuals:
    words = item.split()
    place = words[-1]
    if place in country.keys():
        place = country[place]
    diplomat = " ".join(words[0:-1])
    diplomats[place] = diplomat

# ADDING NEW DIPLOMATS TO THE WP PAGE
for key in diplomats:
    if key in first_country:
        ref = '<ref name="' + refname + '">{{Légifrance|base=JORF|url=' + url + '|texte=Remise de lettres de créance du' + decree_date + '}}.</ref>'
        pattern = '(\| {{' + key + '}}\n\|.+\n\| )[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref.+)?\n\| align="right" \| {{tri date)\|\d+\|[\wéè\dû]+\|\d{4}(}} \|{2} )<ref.+'
        page.text = re.sub(pattern, "\\1[[" + diplomats[key] + ']]\\2' + date + '\\3\\4' + ref, page.text)
    elif key in Bruxelles_first:
        ref = '<ref name="' + refname + '" />'
        pattern = '(\| {{' + key + '}}\n\|.+\n\| )[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref.+)?\n\| align="right" \| {{tri date)\|\d+\|[\wéè\dû]+\|\d{4}(}} \|{2} )<ref.+'
        page.text = re.sub(pattern, "\\1[[" + diplomats[
            key] + ']]<ref name=Bruxelles group=N>En résidence à [[Bruxelles]].</ref>\\2' + date + '\\3\\4' + ref,
                           page.text)
    elif key in London_first:
        ref = '<ref name="' + refname + '" />'
        pattern = '(\| {{' + key + '}}\n\|.+\n\| )[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref.+)?\n\| align="right" \| {{tri date)\|\d+\|[\wéè\dû]+\|\d{4}(}} \|{2} )<ref.+'
        page.text = re.sub(pattern, "\\1[[" + diplomats[
            key] + ']]<ref name="Londres" group=N>En résidence à [[Londres]].</ref>\\2' + date + '\\3\\4' + ref,
                           page.text)
    elif key in Bruxelles:
        ref = '<ref name="' + refname + '" />'
        pattern = '(\| {{' + key + '}}\n\|.+\n\| )[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref.+)?\n\| align="right" \| {{tri date)\|\d+\|[\wéè\dû]+\|\d{4}(}} \|{2} )<ref.+'
        page.text = re.sub(pattern,
                           "\\1[[" + diplomats[key] + ']]<ref name="Bruxelles" group=N />\\2' + date + '\\3\\4' + ref,
                           page.text)
    elif key in London:
        ref = '<ref name="' + refname + '" />'
        pattern = '(\| {{' + key + '}}\n\|.+\n\| )[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref.+)?\n\| align="right" \| {{tri date)\|\d+\|[\wéè\dû]+\|\d{4}(}} \|{2} )<ref.+'
        page.text = re.sub(pattern,
                           "\\1[[" + diplomats[key] + ']]<ref name="Londres" group=N />\\2' + date + '\\3\\4' + ref,
                           page.text)
    else:
        ref = '<ref name="' + refname + '" />'
        pattern = '(\| {{' + key + '}}\n\|.+\n\| )[\[{]?[\[{]?.+[\]}]?[\]}]?((<ref.+)?\n\| align="right" \| {{tri date)\|\d+\|[\wéè\dû]+\|\d{4}(}} \|{2} )<ref.+'
        page.text = re.sub(pattern, "\\1[[" + diplomats[key] + ']]\\2' + date + '\\3\\4' + ref, page.text)

page.text = re.sub(r"(après la cérémonie de remise de lettres de créance du) \d{1,2} [\wéèû]+ \d{4}",
                   "\\1" + decree_date,
                   page.text)
# SAVING PAGE
page.save("Ajout des ambassadeurs ayant remis leurs lettres de créances le" + decree_date)
