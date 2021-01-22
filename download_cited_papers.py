# This is a sample Python script.

from scholarly import scholarly, ProxyGenerator
import json
import time
import re
from fuzzywuzzy import fuzz
import random
import os

WAIT = 30
AUTHOR_ID = "h9mjzyYAAAAJ"
NAME = "Orosz Tamás"
DOWNLOAD_FOLDER = 'publications'
filter_pat = re.compile(r"[A-ZÍŰÁÉÚŐÓÜÖ]{1,2}]")


# pg = ProxyGenerator()
# pg.FreeProxies()
# scholarly.use_proxy(pg)

def save_json(title, publication):
    """
    Saves the citers of the downloaded publication into a json file.

    :param title: title of the document 
    :param publication: list of the collected citing publications
    :return: 
    """
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    with open(DOWNLOAD_FOLDER + "/" + title.replace(" ", "_") + ".json", "w", encoding="utf-8") as file:
        json.dump(publication, file, ensure_ascii=False, indent=4)


def print_citations(res_dict, threshold=70):
    """
     Which papers cited that publication?
     # print([citation['bib']["author"] for citation in scholarly.citedby(pub)])  # ['title']
    :param res_dict:
    :param threshold:
    :return:
    """
    author = res_dict["author"]
    citations = res_dict['cited_this']
    if isinstance(author, str):
        names = [name.strip() for name in author.split("and")]
    elif isinstance(author, list):
        names = author
    independent_citations = []

    for idx, citer_article in enumerate(citations):
        cit_au = citer_article["author"]
        print("%%%%%%%%%%%%%%%%%%%%\n{}. cikk\nCited by {}\n%%%%%%%%%%%%%%%%%%%%".format(idx + 1, cit_au))
        independent = True
        for aut in cit_au:
            for name in names:
                ratio = fuzz.ratio(name, aut)
                partial_ratio = fuzz.partial_ratio(name, aut)
                if partial_ratio > threshold:
                    print("{} vs. {} Ratio: {}, P. ratio:{}".format(name, aut, ratio, partial_ratio))
                    independent = False

        if independent:
            independent_citations.append(citer_article)
    return independent_citations


def download_citations():
    # Retrieve the author's data, fill-in, and print
    # search_query = scholarly.search_author(NAME)
    search_query = scholarly.search_author_id(AUTHOR_ID)
    # author = scholarly.fill(next(search_query))
    author = scholarly.fill(search_query)
    print(author)

    # Print the titles of the author's publications
    print([pub['bib']['title'] for pub in author['publications']])

    # Take a closer look at the first publication
    # pub = scholarly.fill(author['publications'][1])
    # print(pub)
    independent_citations = []
    for pub in author['publications'][:]:
        res_dict = {}
        time.sleep(random.randint(WAIT, WAIT * 2))
        pub = scholarly.fill(pub)
        res_dict["title"] = pub['bib']["title"]
        res_dict["year"] = pub['bib']["pub_year"]
        print(pub['bib']["title"])
        res_dict["author"] = [name.strip() for name in pub['bib']["author"].split("and")]
        time.sleep(random.randint(WAIT, WAIT * 2))
        cited_this = scholarly.citedby(pub)
        if cited_this:
            res_dict['cited_this'] = [{"author": citation['bib']["author"], "title": citation['bib']["title"]} for
                                      citation
                                      in
                                      cited_this]
            indep_citations = print_citations(res_dict)
            res_dict['independent_citations'] = indep_citations
            independent_citations.append(
                {"title": res_dict["title"], "author": res_dict["author"], 'independent_citations': indep_citations})
            save_json(res_dict['title'], res_dict)
        else:
            break

    save_json("independent_citations.json", independent_citations)

if __name__ == '__main__':
    download_citations()
