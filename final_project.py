#!/usr/bin/python3
"""
File:       final_project.py
Authors:    Martijn E.N.F.L. Schendstok (s2688174)
            Jannick Akkermans (s3429075)
            Niels Westeneng (s3469735)
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
    pos_lst = []
    for token in parse:
        pos_lst.append(token.pos_)

    if pos_lst[-1] == "VERB" or pos_lst[-2] == "VERB":
        for token in parse:
            if token.lemma_ in ["found","launch","form","reward","award","establish",
                                "make","introduce","write","release","institude"]:
                x = "inception"
            if token.lemma_ in ["die"]:
                x = "date of death"
            if token.lemma_ in ["happen","occur"]:
                x = "point in time"
            if token.lemma_ in ["begin"]:
                x = "start time"
            if token.lemma_ in ["invent","discover","construct"]:
                x = ["time of discovery or invention","inception"]
            if token.lemma_ in ["bear"]:
                x = "date of birth"

            dep = ["nsubjpass","nsubj","prep","poss","compound","advcl"]
            if (token.dep_ in dep or token.head.dep_ in dep) and token.pos_ not in ["DET","VERB"] and token.lemma_ != "first":
                if token.dep_ == "poss":
                    y += token.text + ""
                else:
                    y += token.text + " "

    elif "VERB" in pos_lst:
        for token in parse:
            if token.lemma_ == "launch":
                x = "launch"
            if token.lemma_ == "appear":
                x = "start time"
            if token.lemma_ in ["extinct","out"]:
                x = "end time"
            if token.lemma_ == "award":
                x = "award received"
                z = "point in time"

            if token.dep_ in ["compound","appos","nsubj","nsubjpass","amod"]:
                y += token.text + " "

    else: # "VERB" not in pos_lst:
        for token in parse:
            if token.lemma_ == "end":
                x = "end time"
            if token.lemma_ == "form":
                x = "inception"

            if token.dep_ in ["compound","nsubj","nummod","pobj","dobj","amod"]:
                if token.lemma_ == "birthday":
                    x = "date of birth" 
                elif token.lemma_ == "flight":
                    x = "first flight"
                elif token.lemma_ == "inception":
                    x = "inception"
                elif token.lemma_ in "moon landing":
                    x = "time of spacecraft landing"
                    y = "moon landing"
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
                        'wide ': ['size', 'diameter'],
                        'moon ': 'child astronomical body',
                        'object ': 'has part',
                        'usual ingredient ': 'has part',
                        'field ': 'has part',
                        'symbol ': 'element symbol',
                        'active compound ': 'has active ingredient',
                        'animal protection status ': 'IUCN conservation status',
                        'average period ': 'gestation period',
                        'big mountain ': 'highest point',
                        'high mountain ': 'highest point',
                        'building block ': 'has part',
                        'centre ': 'has part',
                        'conversion ': 'conversion to SI unit',
                        'distance ': 'distance from earth',
                        'estimate diameter ': 'diameter',
                        'high point ': 'highest point',
                        'low point ': 'lowest point',
                        'recent value ': 'numeric value',
                        'origin ': 'named after',
                        'rotational period ': 'orbital period',
                        'salary ': 'net worth',
                        'scientific name ': ['said to be the same as', 'Commons category'],
                        'unit conversion ': 'conversion to SI unit',
                        'study ': 'studied by',
                        'symbolic element ': 'element symbol',
                        'top speed ': 'speed',
                        'unit ': 'recommended unit of measurement',
                        'water discharge ': 'discharge',
                        'kind ': 'subclass of',
                        'member ': ['has part', 'crew member'],
                        'doctorial advisor ': 'doctoral advisor',
                        'planet ': 'child astronomical body',
                        'moons ': 'child astronomical body'}

    for token in parse:

        if ((token.dep_ == "nsubj" or (token.head.dep_ == "nsubj" and
                                       token.dep_ in ["amod", "compound"]))
                and token.pos_ not in ["PRON", "DET", "ADJ"]) and token.text not in ['name', 'number'] and x == '':
            x += token.lemma_ + " "
        elif token.dep_ in ["attr", "pcomp", "acomp", "advmod"] and token.pos_ in ["NOUN", "ADJ", "ADV"] and token.head.lemma_ in ["be", "at"] and x == '':
            x += token.lemma_ + " "
        elif token.dep_ == "nsubj" and token.head.lemma_ in ['be', 'at'] and token.pos_ not in ['PRON', 'DET'] and token.text not in ['name', 'number'] and token.lemma_ not in x and y == '':
            y += token.lemma_ + " "
        elif token.dep_ == "pobj" and token.pos_ == 'DET' and y == '':
            y += token.lemma_ + " "

        if (token.dep_ in ["pobj", "appos", "dobj", "attr"] and token.pos_ in ['PROPN', 'NOUN']  and y == '') or (token.head.dep_ in ["pobj", "ROOT"] and
                                    token.dep_ in ["amod", "compound"] and
                                    token.pos_ not in ["PRON", "DET", "ADJ"]):
            if x == '':
                x += token.lemma_ + " "
            elif y == '' and token.lemma_ not in x:
                y += token.lemma_ + " "
        elif (token.dep_ == "poss" and token.pos_ not in ["DET", "PROPN"]) or (token.head.dep_ == "poss" and
                                      token.dep_ in ["amod", "compound"] and
                                      token.pos_ not in ["PRON", "DET"]) and y == '':
            y += token.lemma_ + " "

        if token.dep_ in ["compound", "amod"] and token.head.dep_ == "nsubj" and token.pos_ not in ['ADJ'] and token.lemma_ not in x and y == '':
            y += token.lemma_ + " "
        elif token.dep_ == "compound" and token.head.dep_ in ['dobj', 'attr'] and x == '':
            x += token.lemma_ + " " + token.head.lemma_ + " "
        elif token.dep_ in ["compound", "amod"] and token.head.dep_ in ["pobj", "attr", "poss"] and token.lemma_ not in x and token.head.lemma_ not in x:
            y = token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ == "nummod" and token.head.dep_ in ["nmod", "attr", "pobj"]:
            y = token.head.text + " " + token.lemma_ + " "

        if token.pos_ == "ADJ" and token.head.pos_ == "NOUN" and token.head.head.pos_ == "NOUN":
            x += token.lemma_ + " " + token.head.lemma_ + " " + token.head.head.lemma_ + " "

        if token.pos_ == "ADJ" and token.head.pos_ == "NOUN":
            if x == '':
                if token.text in ['sixth', 'seventh', 'third', 'second', 'fourth']:
                    x += token.head.lemma_ + " "
                    z = token.text
                else:
                    x += token.lemma_ + " " + token.head.lemma_ + " "
            elif y == '' and token.lemma_ not in x:
                y += token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ == 'poss' and token.head.dep_ == 'nsubj' and y == '':
            y += token.lemma_ + " "

        if token.pos_ in ["PROPN"] and token.head.pos_ == "ADP" and token.head.head.pos_ == "NOUN" and y == '':
            y = token.head.head.lemma_ + " " + token.head.lemma_ + " " + token.lemma_ + " "
        if token.dep_ == 'compound' and token.head.dep_ == 'compound' and token.head.head.dep_ == 'nsubj' and x == '':
            x = token.lemma_ + " " + token.head.lemma_ + " " + token.head.head.lemma_ + " "
        if token.lemma_ in ['birth', 'work', 'death'] and token.head.lemma_ == 'of' and token.head.head.lemma_ in ['date', 'field', 'place', 'cause']:
            x = token.head.head.lemma_ + " " + token.head.lemma_ + " " + token.lemma_ + " "

        if token.dep_ in ['amod', 'compound'] and token.head.dep_ == 'nsubj' and x == '':
            x = token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ in ['pobj'] and token.head.dep_ in ['acomp'] and y == '':
            y += token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ in ['appos', 'nsubjpass']:
            y = token.lemma_

        if token.text == 'invented':
            x = ["time of discovery or invention", "inception"]
        elif token.text in ["placed", "located"]:
            x = "part of" + " "
        elif token.text == 'children':
            x = 'child'
        elif token.text == 'parts':
            x = 'has part'
        elif token.text == 'died':
            x = 'date of death'
        elif token.text == 'products':
            x = 'product or material produced'
        elif token.text == 'maximally':
            z = "MAXIMUM"
        elif token.text == 'number':
            z = "COUNT"
        elif token.text == 'triangles':
            y = 'triangle'
        elif token.text == 'bronze':
            y = 'bronze'
        elif token.text == 'pancake':
            y = 'pancake'
        elif token.text == 'Advil':
            y = 'Advil'
        elif token.text == 'Tylenol':
            y = 'Tylenol'
        elif token.text == 'robins':
            y = 'European robin'
        elif token.text == 'Zr':
            y = 'zirconium'
        elif token.text == 'lion':
            y = 'lion'
        elif token.text == 'mitochondrion':
            y = 'mitochondrion'
        elif token.text == 'neptune':
            y = 'neptune'
        elif token.text == 'Moon':
            y = 'moon'
        elif token.text == 'CERN':
            y = 'CERN'
        elif token.text == 'Avogadro':
            y = 'Avogadro constant'
        elif token.text == 'paracetamol':
            y = 'paracetamol'
        elif token.text == 'sun':
            y = 'sun'
        elif token.text == 'elephant':
            y = 'elephant'
        elif token.text == 'Nicolas':
            y = 'Nicolas Tesla'
        elif token.text == 'Isaac':
            y = 'Isaac Newton'
        elif token.text in ['Saturn', 'saturn']:
            y = 'Saturn'

        if y == "Moon " and x == "far ":
            x = "distance from Earth" + " "
        elif y in ['light year', 'astronomical unit']:
            x = 'conversion to SI unit' + " "
        elif x == 'type ':
            x = ['followed by', 'subclass of']
        elif y == 'Inner Solar ':
            y = 'Inner Solar System'
        elif y == 'horsepower ':
            y = 'Metric horsepower'
        elif y == 'liquid potassium ':
            y = 'potassium'
        elif x == 'surface ':
            x = "area" + " "
        elif y == 'discharge of Rhine ':
            y = 'Rhine'
        elif y == 'Wide web ':
            y = 'World Wide web'
        elif y == 'Pythagoras ':
            y = 'Pythagoras theorem'

        if 'definition' in x:
            x = ''

    try:
        x = translation_dict[x]
    except KeyError:
        pass
    except TypeError:
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


def is_how_question(parse):
    if parse[0].lemma_ == "how" and parse[1].lemma_ != "many":
        return True
    return False


def how_question(parse, x, y, z):
    for token in parse:
        if token.head.lemma_ == "die":
            x = "manner of death"
        if token.head.lemma_ == "weigh":
            x = "mass"
        if token.head.lemma_ == "call":
            x = ["practiced by", "has part", "Commons category"]
        if token.head.lemma_ == "far":
            x = "distance from Earth"
        if token.head.lemma_ == "run":
            x = "speed"
        if token.head.lemma_ == "boil":
            x = "boiling point"
        if token.head.lemma_ == "emit":
            x = "luminosity"
        if token.head.lemma_ == "embody":
            x = "embodied energy"
        if token.lemma_ == "old":
            x = "highest observed lifespan"
        if token.head.lemma_ == "incubate" and token.lemma_ == "maximally":
            x = "maximal incubation period in humans"
        if token.lemma_ in ["orbit", "revolution", "revolve", "rotation"]:
            x = "orbital period"
        if token.head.lemma_ == "measure":
            x = "recommended unit of measurement"
        if token.head.lemma_ == "define":
            x = ''
        if token.head.lemma_ == "describe" and token.lemma_ == "shape":
            x = "shape"
        

        if token.dep_ in ["nsubj"] and token.pos_ not in ['PRON', 'SCONJ', 'ADJ'] and token.head.dep_ in ['ROOT', 'advcl']:
            y += token.lemma_ + " "
        if token.dep_ in ["nsubjpass"]:
            rc = 0
            for token2 in parse:
                if token2.dep_ in ['nsubj', 'pobj']:
                    rc += 1
            if rc == 0:
                y += token.text + " "
        if token.dep_ in ['pobj'] and len(y) == 0 and token.head.dep_ in ['ROOT']:
            y += token.lemma_ + " "
        if token.dep_ in ['dobj'] and (token.head.dep_ in ['relcl'] or token.pos_ in ['PROPN']):
            y += token.lemma_ + " "
        if token.dep_ in ['compound']:
            if token.head.dep_ == 'nsubj':
                if token.head.lemma_[0].isupper():
                    if token.lemma_[0].isupper():
                        y += token.text + " "
                else:
                    y += token.text + " "
            elif token.head.dep_ == 'pobj':
                if len(y) == 0 and token.head.head.dep_ == "ROOT":
                    y += token.text + " "
    if y == 'emu ':
        y = 'emu alfa'

    return x,y,z


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
    
    elif is_how_question(parse):
        # How question:
        if print_info: print("How question")
        x, y, z = how_question(parse, x, y, z)

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

    if z and z not in ['sixth', 'seventh', 'third', 'second', 'fourth']:
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
    return query, z


def get_answer(query, z):
    """
    Returns the wikidata answer to the given query.
    :param query:       string
    :return answer:     list
    """

    number_dict = {'first': 0,
                   'second': 1,
                   'third': 2,
                   'fourth': 3,
                   'fifth': 4,
                   'sixth': 5,
                   'seventh': 6}

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    url = 'https://query.wikidata.org/sparql'
    r = requests.get(url,
                     headers=headers,
                     params={'query': query, 'format': 'json'})
    data = r.json()
    try:
        z_index = number_dict[z]
    except KeyError:
        z_index = ''

    try:
        answer = list()
        for item in data['results']['bindings']:
            answer.append(item['answerLabel']['value'])
    except KeyError:
        answer = [data["boolean"]]

    if z_index != '':
        try:
            answer_new = list()
            answer_new.append(answer[z_index])
            return answer_new
        except IndexError:
            answer_new = False
            return answer_new
    else:
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
                                answer = get_answer(query, z)
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
                            answer = get_answer(query, z)
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
                        answer = get_answer(query, z)
                        if answer:  # If an answer is found return it
                            if answer[0] or (i == 2 and j == 2):  # Due to False given if nothing found
                                return answer

            else:
                query = get_query(None, y_id, None)
                answer = get_answer(query, z)
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
