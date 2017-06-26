# -*- coding: UTF-8 -*-
"""
rvt_journal_parser
find specific messages in a given journal file
to detect model corruption, missing links and the like.
"""
model_corrupt = 'CorruptElemStream'
missing_links = 'TaskDialog "Revit could not find or read'
key_phrases = {missing_links: "missing_links",
               model_corrupt: "corrupt",
               }


def read_journal(journal_path):
    """
    reads journal file to detect key phrases
    :param journal_path: journal file path
    :return:dict
    """
    detected = {}
    with open(journal_path, 'rb') as journal:
        for line in journal:
            decoded_line = line.decode("latin1", "ignore")
            if model_corrupt in decoded_line:
                print("!!_Corrupt_Model_!!")
                print(journal_path)
                print(decoded_line)
                detected[journal_path] = key_phrases[model_corrupt]
            if missing_links in decoded_line:
                print("!!_Missing_Links_!!")
                print(journal_path)
                print(decoded_line)
                detected[journal_path] = key_phrases[missing_links]
    return detected
