#!/usr/bin/python3
"""
File:       s2688174.py
Author:     Martijn E.N.F.L. Schendstok
Date:       15 May 2020
"""

import sys
import requests
import spacy


def print_example_queries():
    print("1)  What is the taxon name of the lion?")
    print("2)  What is the moon's surface gravity?")
    print("3)  What is the orbital period of the Earth? ")
    print("4)  Where was Nikola Tesla born?")
    print("5)  Where did Albert Einstein die?")
    print("6)  What is a brain?")
    print("7)  Who was F. D. C. Willard?")
    print("8)  Is HTML a markup language?")
    print("9)  Is chloroform a carcinogen?")
    print("10) Who discovered radium?")
    print("11) Who invented the internet?\n")
    print("12) What are the symptoms of influenza?\n")


def print_token_info(token):
    print("{0:<10}{1:<10}{2:<10}{3:<10}{4:<10}{5:<10}{6}".format(token.text,
                                                                 token.lemma_,
                                                                 token.pos_,
                                                                 token.dep_,
                                                                 token.head.lemma_,
                                                                 token.head.dep_,
                                                                 list(token.subtree)))


def get_x_y(question, print_info=False):
    """
    Gets X and Y from questions using spacy
    :param question:    string
    :return x, y:       string, string
    """

    nlp = spacy.load('en_core_web_sm')
    parse = nlp(question)
    x = ""
    y = ""
    z = ""

    if print_info:
        for token in parse:
            print_token_info(token)

    if parse[0].lemma_ == "where":
        # Where question:
        if print_info: print("Where question")
        for token in parse:
            if token.head.lemma_ == "be":
                x = "location"
            # Place of birth:
            if token.head.lemma_ == "bear":
                x = "place of birth"
            # Place of death:
            if token.head.lemma_ == "die":
                x = "place of death"

            if token.dep_ in ["nsubj", "nsubjpass"] or (token.head.dep_ in ["nsubj", "compound"] and
                                                        token.dep_ in ["amod", "compound"]):
                y += token.text + " "
        if not x: x = "location"

    elif parse[0].head.lemma_ == "be" and parse[0].head.dep_ == "ROOT":
        prep = False
        for t in parse[:-2]:
            if t.dep_ == "prep" or (t.head.pos_ == "NOUN" and
                                    t.dep_ == "case"):  # -X of Y- or -X's Y-
                prep = True
        if prep:
            # X of Y question
            if print_info: print("X of Y question")
            for token in parse:

                if ((token.dep_ == "nsubj" or (token.head.dep_ == "nsubj" and
                                               token.dep_ in ["amod", "compound"]))
                        and token.pos_ not in ["PRON", "DET"]):
                    x += token.lemma_ + " "
                elif token.dep_ == "attr" and token.pos_ == "NOUN" and token.head.lemma_ == "be":
                    x += token.lemma_ + " "

                if token.dep_ == "pobj" or (token.head.dep_ == "pobj" and
                                            token.dep_ in ["amod", "compound"] and
                                            token.pos_ not in ["PRON", "DET"]):
                    y += token.text + " "
                elif token.dep_ == "poss" or (token.head.dep_ == "poss" and
                                              token.dep_ in ["amod", "compound"] and
                                              token.pos_ not in ["PRON", "DET"]):
                    y += token.text + " "

        else:
            if parse[0].lemma_ == "be":
                # True/False question:
                if print_info: print("True/False question")
                for token in parse:
                    if ((token.dep_ in ["attr", "appos", "acomp"] and token.head.dep_ in ["ROOT", "nsubj"]) or
                            (token.head.dep_ == "attr" and token.dep_ == "amod")):
                        z += token.text + " "
                    elif token.dep_ in ["nsubj", "compound", "nmod"] and (
                            token.head.dep_ in ["attr", "appos", "nsubj"] or
                            token.pos_ in ["VERB", "PROPN", "NOUN"]):
                        y += token.lemma_ + " "

            elif parse[1].lemma_ == "be":
                # Description question:
                if print_info: print("Description question")
                for token in parse:
                    if token.pos_ in ["NOUN", "PROPN"] or (token.pos_ == "ADJ" and
                                                           token.head.pos_ == "NOUN"):
                        y += token.text + " "


    elif parse[0].lemma_ == "who":
        # Who question:
        if print_info: print("Who question")
        for token in parse:

            if token.pos_ == "VERB":
                vowels = ["a", "e", "i", "o", "u"]
                if token.lemma_[-1] in vowels:
                    x = token.lemma_ + "r"
                elif token.lemma_[-1] == "t":
                    x = token.lemma_ + "or"
                else:
                    x = token.lemma_ + "er"

            if token.pos_ in ["NOUN", "PROPN"]:
                y += token.text + " "

    if print_info: print("x =", x, "\t y =", y, "\t z =", z)
    return x.strip(), y.strip(), z.strip()


def get_wiki_id(token, type="entity", x=0):
    """
    Returns the possible wiki id for an entity (standard) or property.
    :param token:       string
    :param type:        string
    :return wiki_id:    string
    """

    if not token: return None

    url = "https://www.wikidata.org/w/api.php"
    params = {"action": "wbsearchentities",
              "language": "en",
              "format": "json",
              "search": token.rstrip()}

    if type == "property":
        params["type"] = "property"

    json = requests.get(url, params).json()
    try:
        wiki_id = json["search"][x]["id"]
    except IndexError:
        # In case no ID was found
        wiki_id = None
    return wiki_id


def get_query(x, y, z):
    """
    Creates a query for the formats:
        - Is Y Z
        - X of Y
        - Description of Y
    :param x:           string
    :param y:           string
    :param z:           string
    :return query:      string
    """

    #print(x, y, z)

    if z:
        query = "ASK WHERE {"
        query += "wd:{0} (wdt:P279|wdt:P31|wdt:P21)/wdt:P279* wd:{1} .".format(y, z)
        query += "}"

    else:
        query = '''
                SELECT ?answerLabel WHERE {
                '''
        if x:
            query += "wd:{0} wdt:{1} ?answer.".format(y, x)
        else:
            query += '''
                     wd:{0} schema:description ?answer.
                     FILTER(LANG(?answer) = "en")
                     '''.format(y)
        query += '''
                 SERVICE wikibase:label {
                     bd:serviceParam wikibase:language "en".
                     }
                 }
                 '''
    return query


def get_answer(query):
    """
    Returns the wikidata answer to the given query.
    :param query:       string
    :return answer:     list
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    url = 'https://query.wikidata.org/sparql'
    r = requests.get(url,
                     headers=headers,
                     params={'query': query, 'format': 'json'})
    data = r.json()
    try:
        answer = list()
        for item in data['results']['bindings']:
            answer.append(item['answerLabel']['value'])
    except KeyError:
        answer = [data["boolean"]]

    return answer


def create_and_fire_query(question):
    """
    Get query for the given question and get the answer using the question
    :param question:    string
    :return answer:     list
    """

    x, y, z = get_x_y(question)
    for j in range(3):  # Check top 3 entity options
        # Check bi-grams as well if y contains more than 2 tokens:
        y_list = [y]
        y_tokens = y.split()
        if len(y_tokens) > 2:
            for i in range(len(y_tokens) - 1):
                y_list.append(" ".join((y_tokens[i], y_tokens[i + 1])))

        for y in y_list:
            y_id = get_wiki_id(y, type="entity", x=j)
            if x:
                for i in range(3):  # Check top 3 property options
                    x_id = get_wiki_id(x, type="property", x=i)
                    if x_id and y_id:
                        query = get_query(x_id, y_id, None)
                        answer = get_answer(query)
                        if answer:  # If an answer is found return it
                            return answer

            elif z:
                for i in range(3):  # Check top 3 property options
                    z_id = get_wiki_id(z, type="entity", x=i)
                    if y_id and z_id:
                        query = get_query(None, y_id, z_id)
                        answer = get_answer(query)
                        if answer:  # If an answer is found return it
                            if answer[0] or (i == 2 and j == 2):  # Due to False given if nothing found
                                return answer

            else:
                query = get_query(None, y_id, None)
                answer = get_answer(query)
                if answer:  # If an answer is found return it
                    return answer

    return ["Could not find an answer"]


def main(argv):
    print("Possible question types:\n"
          "- X of Y questions\n"
          "- X's Y questions\n"
          "- Where questions\n"
          "- Who questions\n"
          "- True/False questions\n"
          "- Description questions\n"
          "\n"
          "Examples:")
    print_example_queries()
    print("# Input a question:")
    for line in sys.stdin:
        line = line.rstrip()  # removes newline
        answer = create_and_fire_query(line)
        if answer:
            for ans in answer:
                print(ans)


if __name__ == "__main__":
    main(sys.argv)
