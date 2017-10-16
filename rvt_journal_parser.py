# -*- coding: UTF-8 -*-
"""
rvt_journal_parser
find specific messages in a given journal file
to detect model corruption, missing links and the like.
"""
import os.path as op
import colorful

model_corrupt = 'orrupt'
missing_links = 'TaskDialog "Revit could not find or read'
circular_links = 'TaskDialog_Circular_Link_Conflict'
key_phrases = {missing_links: "missing_links",
               model_corrupt: "corrupt",
               circular_links: "circular links",
               }


def read_journal(journal_path):
    """
    reads journal file to detect key phrases
    :param journal_path: journal file path
    :return:dict
    """
    detected = {}
    with open(journal_path, 'rb') as journal:
        journal_name = op.basename(journal_path)
        for line in journal:
            decoded_line = line.decode("latin1", "ignore")
            for key_phrase in key_phrases:
                if key_phrase in decoded_line:
                    print(colorful.bold_red(f"-!!_found:{key_phrases[key_phrase]}_!!"))
                    print(" journal path: {}".format(journal_path))
                    # print(decoded_line)
                    detected[key_phrases[key_phrase]] = journal_name + decoded_line
                    return detected
    if not detected:
        detected["nothing detected in"] = journal_name
        return detected
