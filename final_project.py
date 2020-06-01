#!/usr/bin/python3
"""
File:       final_project.py
Authors:    Martijn E.N.F.L. Schendstok (s2688174)
            Jannick Akkermans (s3429075)
            Niels
            Mariska de Vries (s3483630)
Date:       26 May 2020
"""

import sys
import requests
import spacy


def print_token_info(token):
    print("{0:<12}{1:<14}{2:<12}{3:<12}{4:<18}{5:<18}{6}".format(token.text,
                                                                 token.lemma_,
                                                                 token.pos_,
                                                                 token.dep_,
                                                                 token.head.lemma_,
                                                                 token.head.dep_,
                                                                 list(token.subtree)))


def is_where_question(parse):
    if parse[0].lemma_ == "where":
        return True
    return False


def where_question(parse, x, y, z):
    in_status = False
    earth_status = False
    c = 0
    for token in parse:
        if c == 1:
            if token.lemma_ == "in":
                in_status = True
        c += 1
        if token.lemma_ == "earth" and token.head.lemma_ == "on":
            earth_status = True
            print(token.text, token.head.text, earth_status)
        if token.head.lemma_ == "be":
                x = ['recommended unit of measurement', 'anatomical location', 'part of', 'location']            
        # Place of birth:
        if token.head.lemma_ == "bear" or token.text == "birthplace":
            x = "place of birth"
        # Place of death:
        if token.head.lemma_ == "die":
            x = "place of death"
        # Studied at
        if token.head.lemma_ == "study":
            x = "student of"
        # Work for
        if token.head.lemma_ == "work":
            x = "employer"
        # Live at
        if token.head.lemma_ == "live":
            x = "residence"
        # Come from
        if token.head.lemma_ == "come":
            x = ["country of origin", "endemic to"]
        # Place of burying
        if token.head.lemma_ == "bury":
            x = "place of burial"
        # Location of Headquarters
        if token.head.lemma_ == "headquarter" or token.text == "headquarters":
            x = "headquarters location"
        # Education
        if token.head.lemma_ == "educate":
            x = "educated at"
        # Place made
        if token.head.lemma_ == "make":
            x = "country"
        # Forming location
        if token.head.lemma_ == "form":
            x = "location of formation"
        # Place in body
        if token.head.lemma_ == "locate":
            x = "anatomical location"
        # Place in body
        if token.head.lemma_ == "find":
            x = "part of"
        # Used for
        if token.head.lemma_ == "use":
            x = "use"
        # Place of disovery
        if token.head.lemma_ == "discover":
            x = "location of discovery"

        if (token.dep_ in ["nsubj", "nsubjpass"] and token.pos_ not in ['PRON'] and token.lemma_ not in ["birthplace", "headquarters"]) or (token.head.dep_ in ["nsubj", "pobj", "compound"] and token.dep_ in ["amod", "compound"]) or token.dep_ in ['dobj'] or (token.dep_ in ['pobj'] and token.pos_ in ['PROPN']) or (token.lemma_ == "covid-19" and token.dep_ == "punct") or (in_status and token.dep_ == "attr") or (in_status and token.head.dep_ == "attr" and token.dep_ == 'amod'):
            y += token.text + " "
    if earth_status:
        y = "earth"
        x = ""
        x_t = ""
        for token in parse:
            if (token.pos_ == "NOUN" and token.dep_ in ["nsubj", "attr"]) or (token.head.pos_ == "NOUN" and token.head.dep_ in ["nsubj", "attr"] and token.dep_ == "amod"):
                x_t += token.lemma_ + " "
        if "temperature" in x_t and ("hot" in x_t or "maximum" in x_t or "high" in x_t):
            x = "maximum temperature record"
    if not x: x = "location"

    return x, y, z


def is_when_question(parse):
    if parse[0].lemma_ == "when":
        return True
    return False


def when_question(parse, x, y, z):
    for token in parse:
        if token.pos_ == "VERB":
            if token.lemma_ in ["invent","discover","construct"]:
                x = "time of discovery or invention"

            if token.lemma_ == "bear":
                x = "date of birth"

            if token.lemma_ == "die":
                x = "date of death"

            if token.lemma_ == "begin":
                x = "start time"

            if token.lemma_ == "end":
                x = "end time"

            if token.lemma_ in ["happen","occur"]:
                x = "point in time"

            if token.lemma_ not in ["invent","discover","construct","bear","die","happen","occur","begin","end",]:
                x = "inception"

        if token.pos_ in ["ADJ","NOUN", "PROPN"] and token.lemma_ != "first":
            if token.lemma_ == "birthday":
                x = "date of birth"

            else:
                y += token.text + " "

    if x == "":
        x = "point in time"

    return x, y, z


def is_xy_question(parse):
    if (parse[0].head.lemma_ in ["be", "move", "name"] and parse[0].head.dep_ == "ROOT") or (parse[1].head.lemma_ in ["be", "move"] and parse[1].head.dep_ == "ROOT"):
        prep = False
        for t in parse[:-2]:
            if t.dep_ in ["prep", "advmod"] or (t.head.pos_ == "NOUN" and
                                    t.dep_ == "case"):  # -X of Y- or -X's Y-
                prep = True
        if prep:
            return True
    return False


def xy_question(parse, x, y, z):
    translation_dict = {'big ': ['diameter', 'mass'],
                        'deep ': 'elevation',
                        'dense ': 'density',
                        'heavy ': 'mass',
                        'hot ': 'temperature',
                        'large ': ['size', 'diameter'],
                        'old ': ['inception', 'start time'],
                        'tall ': 'height',
                        'wide ': ['size', 'diameter']}
    for token in parse:

        if ((token.dep_ == "nsubj" or (token.head.dep_ == "nsubj" and
                                       token.dep_ in ["amod", "compound"]))
                and token.pos_ not in ["PRON", "DET"]) and x == '':
            x += token.lemma_ + " "
        elif token.dep_ in ["attr", "pcomp", "acomp", "advmod"] and token.pos_ in ["NOUN", "ADJ", "ADV"] and token.head.lemma_ in ["be", "at"] and x == '':
            x += token.lemma_ + " "
        elif token.dep_ == "nsubj" and token.head.lemma_ in ['be', 'at'] and token.pos_ not in ['PRON'] and y == '':
            y += token.lemma_ + " "

        if (token.dep_ == "pobj" and token.pos_ in ['PROPN'] and y == '') or (token.head.dep_ in ["pobj", "ROOT"] and
                                    token.dep_ in ["amod", "compound"] and
                                    token.pos_ not in ["PRON", "DET"]):
            y += token.lemma_ + " "
        elif (token.dep_ == "poss" and token.pos_ != "DET") or (token.head.dep_ == "poss" and
                                      token.dep_ in ["amod", "compound"] and
                                      token.pos_ not in ["PRON", "DET"]) and y == '':
            y += token.lemma_ + " "

        if token.dep_ in ["compound", "amod"] and token.head.dep_ == "nsubj" and y == '':
            y += " ".join([tok.text for tok in token.head.subtree if tok.text not in ['-']][1:])
        elif token.dep_ == "compound" and token.head.dep_ in ['dobj', 'attr']:
            x += token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ == "nummod" and token.head.dep_ == "nmod":
            y += token.head.text + " " + token.lemma_ + " "

        if token.text == 'surface':
            x = "area" + " "
        elif token.text == 'maximally':
            z = "MAXIMUM"

        if y == "Moon " and x == "far ":
            x = "distance from Earth" + " "
        elif y in ['light year', 'astronomical unit']:
            x = 'conversion to SI unit' + " "

    try:
        x = translation_dict[x]
    except KeyError:
        pass

    return x, y, z


def is_truefalse_question(parse):
    if not is_xy_question(parse) and parse[0].lemma_ == "be":
        return True
    return False


def truefalse_question(parse, x, y, z):
    for token in parse:
        if ((token.dep_ in ["attr", "appos", "acomp"] and token.head.dep_ in ["ROOT", "nsubj"]) or
                (token.head.dep_ == "attr" and token.dep_ == "amod")):
            z += token.text + " "
        elif token.dep_ in ["nsubj", "compound", "nmod"] and (
                token.head.dep_ in ["attr", "appos", "nsubj"] or
                token.pos_ in ["VERB", "PROPN", "NOUN"]):
            y += token.lemma_ + " "

    return x, y, z


def is_description_question(parse):
    if not is_xy_question(parse) and parse[1].lemma_ == "be" and not parse[1].dep_ == "auxpass":
        return True
    return False


def description_question(parse, x, y, z):
    for token in parse:
        if token.pos_ in ["NOUN", "PROPN"] or (token.pos_ == "ADJ" and
                                               token.head.pos_ == "NOUN"):
            y += token.text + " "

    return x, y, z


def is_who_question(parse):
    if parse[0].lemma_ == "who":
        return True
    if parse[-2].lemma_ == "whom":
        return True
    return False


def who_question(parse, x, y, z):
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

    return x, y, z


def is_count_question(parse):
    if parse[0].lemma_ == "how" and parse[1].lemma_ == "many":
        return True
    return False


def count_question(parse, x, y, z):
    first = True
    for token in parse:
        if token.pos_ == "NOUN" and first:
            x += token.lemma_ + " "
            if token.dep_ != "compound":
                first = False  # If first noun found second should be appended to y

        elif token.pos_ in ["PROPN", "NOUN"]:
            y += token.text + " "
            if token.pos_ == "PROPN":
                first = True  # If y is a proper noun al other nouns should be appended to x

    if x.strip() == "part": x = "has part"
    if x.strip() == "moon": x = "child astronomical body"
    return x, y, "COUNT"


def get_x_y(question, print_info=False):
    """
    Gets X and Y from questions using spacy
    :param question:    string
    :return x, y, z:    string, string, string
    """

    nlp = spacy.load('en_core_web_sm')
    parse = nlp(question)
    x = ""
    y = ""
    z = ""

    if print_info:
        print("{0:<12}{1:<14}{2:<12}{3:<12}{4:<18}{5:<18}{6}".format("token.text",
                                                                     "token.lemma_",
                                                                     "token.pos_",
                                                                     "token.dep_",
                                                                     "token.head.lemma_",
                                                                     "token.head.dep_",
                                                                     "token.subtree"))
        for token in parse:
            print_token_info(token)

    if is_where_question(parse):
        # Where question:
        if print_info: print("Where question")
        x, y, z = where_question(parse, x, y, z)

    elif is_when_question(parse):
        # When question:
        if print_info: print("When question")
        x, y, z = when_question(parse, x, y, z)

    elif is_xy_question(parse):
        # X of Y question
        if print_info: print("X of Y question")
        x, y, z = xy_question(parse, x, y, z)

    elif is_truefalse_question(parse):
        # True/False question:
        if print_info: print("True/False question")
        x, y, z = truefalse_question(parse, x, y, z)

    elif is_description_question(parse):
        # Description question:
        if print_info: print("Description question")
        x, y, z = description_question(parse, x, y, z)

    elif is_who_question(parse):
        # Who question:
        if print_info: print("Who question")
        x, y, z = who_question(parse, x, y, z)

    elif is_count_question(parse):
        # Count question:
        if print_info: print("Count question")
        x, y, z = count_question(parse, x, y, z)

    if print_info: print("x =", x, "\t y =", y, "\t z =", z)
    print(type(x))
    if type(x) == list:
        return x, y.strip(), z.strip()
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
        if z == "COUNT":
            query = '''SELECT (COUNT (DISTINCT ?item) AS ?answerLabel)
                       WHERE {'''
            query += "wd:{0} wdt:{1} ?item.".format(y, x)
            query += '''
                     SERVICE wikibase:label {
                        bd:serviceParam wikibase:language "en".
                        }
                     }
                     '''
        elif z == "MAXIMUM":
            query = '''SELECT (MAX(?item) as ?answerLabel)
                                   WHERE {'''
            query += "wd:{0} wdt:{1} ?item.".format(y, x)
            query += '''
                                 SERVICE wikibase:label {
                                    bd:serviceParam wikibase:language "en".
                                    }
                                 }
                                 '''
            query += '''ORDER BY ?item'''

        else:
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

    x, y, z = get_x_y(question, print_info=True)
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
                    if type(x) == list:
                        for xx in x:
                            x_id = get_wiki_id(xx, type="property", x=i)
                            print("test", x_id, y_id)
                            if x_id and y_id:
                                query = get_query(x_id, y_id, z)
                                answer = get_answer(query)
                                if z == "COUNT":
                                    if answer[0] != "0":  # As 0 is returned if noting is found for the COUNT
                                        return answer
                                else:
                                    if answer:  # If an answer is found return it
                                        return answer
                    else:
                        x_id = get_wiki_id(x, type="property", x=i)
                        print("test", x_id, y_id)
                        if x_id and y_id:
                            query = get_query(x_id, y_id, z)
                            answer = get_answer(query)
                            if z == "COUNT":
                                if answer[0] != "0":  # As 0 is returned if noting is found for the COUNT
                                    return answer
                            else:
                                if answer:  # If an answer is found return it
                                    return answer

            elif z and z != "COUNT":
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
    print("# Input a question:")
    for line in sys.stdin:
        line = line.strip().split("\t")
        n = line[0]
        question = line[1]
        answer = create_and_fire_query(question)

        # Print output:
        print(n, end="")
        if answer:
            for ans in answer:
                if ans == True: ans = "yes"
                if ans == False: ans = "no"
                print("\t{0}".format(ans), end="")
        print()


if __name__ == "__main__":
    main(sys.argv)
