import json
import os
from collections import OrderedDict
import pandas as pd
from datetime import datetime
from crossref.restful import Works
import requests
import json

FOLDER = "./tomi/"
FILTER_THESE = ["TZ Adam", "TZ Ádám"]


def get_doi(title, author):
    works = Works()
    work = works.query(bibliographic=title, author=author).url
    response = requests.get(work)
    json_response = json.loads(response.text)
    try:
        document = json_response["message"]["items"][0]
        return document.get("URL")  # print(document["DOI"], document["title"], document["URL"])
    except IndexError:
        return None


def collect_independent_citations(json_file, ret_lst):
    cited_docs = json_file["independent_citations"]
    for data_row in cited_docs:
        if not set(FILTER_THESE).intersection(data_row["author"]):
            ordered_dict = OrderedDict()
            ordered_dict["your_works_title"] = json_file["title"]
            ordered_dict["cited_by_authors"] = ", ".join(data_row["author"])
            ordered_dict["cited_by_title"] = data_row["title"]
            ordered_dict["DOI"] = get_doi(data_row["title"], ordered_dict["cited_by_authors"])
            ret_lst.append(ordered_dict)


files = [file for file in os.listdir(FOLDER) if file.endswith(".json")]
ret_lst = []
for file in files:
    file_path = os.path.join(FOLDER, file)
    with open(file_path, encoding="utf-8") as json_file:
        data = json.load(json_file)
    collect_independent_citations(data, ret_lst)
df = pd.DataFrame(ret_lst)
df.to_csv("{}.csv".format(datetime.now().strftime("%Y_%d_%m_%H_%M_%S"), sep=";"))
