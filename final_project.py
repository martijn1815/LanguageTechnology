#!/usr/bin/python3
"""
File:       final_project.py
Authors:    Martijn E.N.F.L. Schendstok (s2688174)
            Jannick Akkermans (s3429075)
            Niels Westeneng (s3469735)
            Mariska de Vries (s3483630)
Date:       9 June 2020
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
    lemma_lst = []
    dep_lst = []
    pos_lst = []
    for token in parse:
        lemma_lst.append(token.lemma_)
        dep_lst.append(token.dep_)
        pos_lst.append(token.pos_)

    for token in parse:
        if token.lemma_ in ["found","form","reward","establish","create","inception",
                            "make","introduce","write","release","institude"]:
            x = "inception"
        if token.lemma_ == "launch":
            x = ["launch", "UTC date of spacecraft launch","inception"]
        if token.lemma_ == "die":
            x = "date of death"
        if token.lemma_ in ["happen","occur"]:
            x = "point in time"
        if token.lemma_ in ["begin","appear"]:
            x = "start time"
        if token.lemma_ in ["end","extinct","out"]:
            x = "end time"
        if token.lemma_ in ["invent","discover","construct"]:
            x = ["time of discovery or invention","inception"]
        if token.lemma_ in ["bear","birthday"]:
            x = "date of birth"
        if token.lemma_ == "award":
            x = ["inception","award received"]
        if token.lemma_ == "flight" and "first" in lemma_lst:
            x = "first flight"
        if token.lemma_ == "landing" and "moon" in lemma_lst:
            x = "time of spacecraft landing"
        if token.lemma_ == "tungsten":
            y = "tungsten"


        if "VERB" in pos_lst: #parse contains a verb
            if token.dep_ == "nsubj" and token.head.dep_ == "relcl":
                y = token.lemma_

            elif token.dep_ == "nsubj" and token.head.lemma_ == "be":
                y = token.lemma_


            elif token.dep_ in ["nsubj","nsubjpass"]:
                for tok in token.subtree:
                    if tok.pos_ not in ["DET"] and tok.lemma_ != "first":
                        if tok.dep_ == "poss":
                            y += tok.text + ""
                        else:
                            y += tok.lemma_ + " "

            elif token.dep_ == "compound" and token.head.dep_ == "ROOT":
                y = token.lemma_

        if "VERB" not in pos_lst: #parse does not contain a verb
            if "pobj" not in dep_lst and "dobj" not in dep_lst:
                if token.dep_ in ["compound","nsubj"]:
                    y += token.lemma_ + " "

            else:
                if token.dep_ in ["compound","pobj","nummod","dobj"]:
                    y += token.lemma_ + " "

    if x == "": #if x does not have a value try point in time
        x = ["point in time","inception","time of discovery or invention"]

    if y != "" and y[-2] == "s" and y[-3] == "e":
        y = y[:-2]

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
    definition = False
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
                        'planet ': ['child astronomical body', 'has part'],
                        'moons ': 'child astronomical body',
                        'solar mass ': 'mass',
                        'boil ': 'boiling point',
                        'different type ': 'has part',
                        'pregnant': 'gestation period',
                        'long ': ['length', 'conversion to SI unit'],
                        'gravity': ['gravity', 'surface gravity'],
                        'warm ': 'temperature',
                        'main component ': 'has part',
                        'material result ': 'product or material produced',
                        'chemical element ': 'has part'}

    for token in parse:

        if ((token.dep_ == "nsubj" or (token.head.dep_ == "nsubj" and
                                       token.dep_ in ["amod", "compound"]))
                and token.pos_ not in ["PRON", "DET", "ADJ"]) and token.lemma_ not in ['name', 'number'] and x == '':
            x += token.lemma_ + " "
        elif token.dep_ in ["attr", "pcomp", "acomp", "advmod"] and token.pos_ in ["NOUN", "ADJ", "ADV"] and token.head.lemma_ in ["be", "at"] and token.lemma_ not in ['how'] and x == '':
            x += token.lemma_ + " "
        elif token.dep_ == "nsubj" and token.head.lemma_ in ['be', 'at', 'boil'] and token.pos_ not in ['PRON', 'DET'] and token.lemma_ not in ['name', 'number'] and token.lemma_ not in x and y == '':
            y += token.lemma_ + " "
        elif token.dep_ == "pobj" and token.pos_ == 'DET' and y == '':
            y += token.lemma_ + " "

        if (token.dep_ in ["pobj", "appos", "dobj", "attr"] and token.pos_ in ['PROPN', 'NOUN'] and token.lemma_ not in x and y == '') or (token.head.dep_ in ["pobj", "ROOT"] and
                                    token.dep_ in ["amod", "compound"] and
                                    token.pos_ not in ["PRON", "DET", "ADJ"]):
            if x == '':
                x += token.lemma_ + " "
            elif y == '' and token.lemma_ not in x and token.text not in ['study', 'degrees', 'part', 'Celsius', 'Leonhard', 'Manhattan', 'Inner']:
                y += token.lemma_ + " "
        elif (token.dep_ == "poss" and token.pos_ not in ["DET", "PROPN"]) or (token.head.dep_ == "poss" and
                                      token.dep_ in ["amod", "compound"] and
                                      token.pos_ not in ["PRON", "DET"]) and y == '':
            y += token.lemma_ + " "

        if token.dep_ in ["compound", "amod"] and token.head.dep_ == "nsubj" and token.pos_ not in ['ADJ'] and token.lemma_ not in x and y == '':
            y += token.lemma_ + " " + token.head.lemma_ + " "
        elif token.dep_ == "compound" and token.head.dep_ in ['dobj', 'attr'] and x == '':
            x += token.lemma_ + " " + token.head.lemma_ + " "
        elif token.dep_ in ["compound", "amod"] and token.head.dep_ in ["pobj", "attr", "poss"] and token.lemma_ not in x and token.head.lemma_ not in x and token.lemma_ not in ['degree'] and y == '':
            y = token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ == "nummod" and token.head.dep_ in ["nmod", "attr", "pobj"] and y == '':
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
            elif y == '' and token.head.lemma_ not in x:
                y += token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ == 'poss' and token.pos_ not in ['DET'] and token.head.dep_ == 'nsubj' and y == '':
            y += token.lemma_ + " "

        if token.pos_ in ["PROPN"] and token.head.pos_ == "ADP" and token.head.head.pos_ == "NOUN" and y == '':
            y = token.head.head.lemma_ + " " + token.head.lemma_ + " " + token.lemma_ + " "
        if token.dep_ == 'compound' and token.head.dep_ == 'compound' and token.head.head.dep_ == 'nsubj' and x == '':
            x = token.lemma_ + " " + token.head.lemma_ + " " + token.head.head.lemma_ + " "
        if token.dep_ == 'compound' and token.head.dep_ == 'compound' and token.head.head.dep_ == 'pobj' and y == '':
            y = token.lemma_ + " " + token.head.lemma_ + " " + token.head.head.lemma_ + " "
        if token.lemma_ in ['birth', 'work', 'death', 'sound', 'citizenship'] and token.head.lemma_ == 'of' and token.head.head.lemma_ in ['date', 'field', 'place', 'cause', 'speed', 'country']:
            x = token.head.head.lemma_ + " " + token.head.lemma_ + " " + token.lemma_ + " "

        if token.lemma_ in ['relativity'] and token.head.lemma_ == 'of' and token.head.head.lemma_ in ['theory']:
            y = token.head.head.lemma_ + " " + token.head.lemma_ + " " + token.lemma_ + " "

        if token.dep_ in ['amod', 'compound'] and token.head.dep_ == 'nsubj' and x == '':
            x = token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ in ['pobj'] and token.head.dep_ in ['acomp'] and y == '':
            y += token.lemma_ + " " + token.head.lemma_ + " "

        if token.dep_ in ['appos', 'nsubjpass'] and token.pos_ not in ['DET'] and y == '':
            y = token.lemma_

        if token.dep_ == 'nummod' and token.head.dep_ in ['compound', 'pobj'] and token.head.lemma_ not in ['parent', 'atm']:
            if token.head.head.dep_ in ['pobj', 'appos']:
                z = token.lemma_ + " " + token.head.lemma_ + " " + token.head.head.lemma_ + " "
            else:
                z = token.lemma_ + " " + token.head.lemma_

        if token.dep_ == 'relcl' and token.pos_ in ['VERB', 'NOUN']:
            x = token.lemma_ + " "

        if token.text == 'invented':
            x = ["time of discovery or invention", "inception"]
        elif token.text in ["placed", "located"]:
            x = "part of" + " "
        elif token.text in ['children', 'pregnant', 'gravity']:
            x = token.lemma_
        elif token.text in ['triangles', 'bronze', 'pancake', 'Advil', 'Tylenol', 'lion', 'mitochondrion', 'neptune', 'CERN', 'paracetamol', 'sun', 'Sun', 'elephant', 'temperature', 'alcohol']:
            y = token.lemma_
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
        elif token.text == 'robins':
            y = 'European robin'
        elif token.text == 'Zr':
            y = 'zirconium'
        elif token.text == 'Moon':
            y = 'moon'
        elif token.text == 'Avogadro':
            y = 'Avogadro constant'
        elif token.text == 'Nicolas':
            y = 'Nicolas Tesla'
        elif token.text == 'Isaac':
            y = 'Isaac Newton'
        elif token.text in ['Saturn', 'saturn']:
            y = 'Saturn'
        elif token.text in ['center', 'centre', 'core'] and z == '':
            z = 'CENTER'
        elif token.text in ['sixth', 'seventh', 'third', 'second', 'fourth']:
            z = token.lemma_
        elif token.text == 'definition':
            definition = True
        elif token.text in ['liquid', 'solid']:
            z = token.text
        elif token.text == 'Solar' and y in ['inner System ', 'Inner System ']:
            y = 'Inner Solar System'
        elif token.text == 'Curie' and y == 'Marie ':
            y = 'Marie Curie'
        elif token.text == 'Nobel' and token.head.lemma_ == 'prize':
            y = 'Nobel prize'
        elif token.text == 'geographical' and token.head.text == 'center':
            z = 'geographical center'

        if y in ["Moon ", "moon ", "Moon", "moon"] and x in ["far ", "far"]:
            x = "distance from Earth" + " "
        elif y in ['solar system ', 'Solar System ', 'solar System ', 'Solar system '] and x == 'planet ':
            y = 'Sun'
        elif y == 'red cell ' and token.lemma_ == 'blood':
            y = 'red blood cell'
        elif y == 'Great Reef ' and token.lemma_ == 'Barrier':
            y = 'Great Barrier Reef'
        elif y in ['light year', 'astronomical unit']:
            x = 'conversion to SI unit' + " "
        elif x == 'type ':
            x = ['followed by', 'subclass of']
        elif y in ['Inner Solar ']:
            y = 'Inner Solar System'
        elif y in ['inner system ', 'Inner System '] and token.lemma_ in ['solar', 'Solar']:
            y = 'Inner Solar System'
        elif y == 'horsepower ':
            y = 'Metric horsepower'
        elif y in ['liquid potassium ', 'solid potassium ']:
            y = 'potassium'
        elif x == 'surface ':
            x = "area" + " "
        elif y == 'discharge of Rhine ':
            y = 'Rhine'
        elif y == 'Wide web ':
            y = 'World Wide web'
        elif y == 'Pythagoras ':
            y = 'Pythagoras theorem'
        elif x == 'dutch word ':
            x = ''
            z = "DUTCH"
        elif y == 'biological cell ':
            y = 'cell'
        elif x == 'official name ':
            z = "LABEL"


    try:
        x = translation_dict[x]
    except KeyError:
        pass
    except TypeError:
        pass

    if definition:
        x = ''

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
    if parse[-2].lemma_ in ["whom","who"]:
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


def is_in_question(parse):
    if parse[0].lemma_ == "in":
        return True
    return False


def in_question(parse, x, y, z):
    for token in parse:
        if token.head.lemma_ == "bear":
            x = "place of birth"
        if token.head.lemma_ == "country":
            x = "country"
        if token.head.lemma_ == "work":
            x = "field of work"
        if token.head.lemma_ == "language":
            x = "languages spoken, written or signed"
        if token.head.lemma_ == "found":
            x = "inception"
        if token.head.lemma_ == "measure":
            x = "measurement scale"
        if token.head.lemma_ == "find":
            x = ["anatomical location", "part of"]
        if token.head.lemma_ == "publish":
            x = "publication date"
        if token.head.lemma_ in ["discover", "invent"]:
            x = ["time of discovery or invention", "inception"]


        if token.dep_ in ["nsubj", "nsubjpass"] and token.pos_ != "PRON" and token.lemma_ not in ["country"]:
            y += token.lemma_ + " "
        if token.dep_ == "dobj":
            y += token.text + " "
        if token.dep_ == "compound" and token.head.dep_ in ["nsubj", "dobj"]:
            y += token.text + " "

    return x,y,z


def is_what_do_question(parse):
    if parse[0].lemma_ == "what":
        for token in parse:
            if token.lemma_ == "do":
                return True
        return False
    return False


def what_do_question(parse, x, y, z):
    c = 0
    for token in parse:
        c += 1
        if token.head.lemma_ == "do":
            x = "occupation"
        if token.head.lemma_ == "die":
            x = "cause of death"
        if token.head.lemma_ in ["consist", "part"]:
            x = ["material used", "has part"]
        if token.head.lemma_ == "study":
            x = "studies"
        if token.head.lemma_ == "stand":
            x = ["official name",""]
        if token.head.lemma_ == "solve":
            x = "solves"
        if token.head.lemma_ == "mean":
            x = ""
        if token.head.lemma_ == "belong":
            x = "instance of"
        if token.head.lemma_ == "call":
            x = "practiced by"
        if token.lemma_ == "interaction":
            x = "interaction"
        if token.head.lemma_ == "speak":
            x = "Languages spoken, written or signed"
        if token.head.lemma_ == "mass":
            x = "mass"
        if token.head.lemma_ == "win":
            x = "awards received"
        if token.head.lemma_ == "shape":
            x = "shape"
        if token.head.lemma_ == "sound":
            x = "produced sound"
        if token.head.lemma_ == "temperature":
            x = "temperature"
            for token2 in parse:
                if token2.lemma_ in ["centre", "core"]:
                    z = "centre"
        if token.head.lemma_ == "work":
            x = "employer"

        if token.lemma_ != "what" and c > 2:
            if token.dep_ in ["nsubj", "nsubjpass", "csubj"] and token.pos_ != "PRON":
                y += token.lemma_ + " "
            if token.dep_ in ["dobj", "pobj"]:
                status = True
                for token2 in parse:
                    if token2.dep_ in ["nsubj", "nsubjpass", "csubj"] and token.pos_ != "PRON":
                        status = False
                if status:
                    y += token.text + " "
            if token.dep_ == "compound" and token.head.dep_ in ["nsubj", "dobj", "pobj"]:
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


def if_at_what_question(parse):
    if parse[0].lemma_ == "at" and parse[1].lemma_ == "what":
        return True
    return False


def at_what_question(parse, x, y, z):
    meltingpoint_list = [token.lemma_ for token in parse]
    if "temperature" in meltingpoint_list and "melt" in meltingpoint_list:
        x = "melting point"

        for token in parse:
            if token.pos_ in ["NOUN", "PROPN"] and token.lemma_ != "temperature":
                y += token.lemma_ + " "

    return x, y, z


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

    elif is_in_question(parse):
        # In question:
        if print_info: print("In question")
        x, y, z = in_question(parse, x, y, z)

    elif is_what_do_question(parse):
        # In question:
        if print_info: print("What do question")
        x, y, z = what_do_question(parse, x, y, z)

    elif if_at_what_question(parse):
        x, y, z = at_what_question(parse, x, y, z)

    if print_info: print("x =", x, "\t y =", y, "\t z =", z)
    if print_info: print("Type of x:", type(x))
    if y.strip() == "black plague":
        y = "black death"
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

        elif z == "CENTER":
            query = '''
                    SELECT ?answerLabel WHERE {
                    '''
            query += "wd:{0} p:{1} ?statement.".format(y, x)
            query += '''?statement ps:{0} ?answer;'''.format(x)
            query += '''pq:P518 wd:Q23595.'''
            query += '''
                                             SERVICE wikibase:label {
                                                bd:serviceParam wikibase:language "en".
                                                }
                                             }
                                             '''
        elif z == 'geographical center':
            query = '''
                                SELECT ?answerLabel WHERE {
                                '''
            query += "wd:{0} p:{1} ?statement.".format(y, x)
            query += '''?statement ps:{0} ?answer;'''.format(x)
            query += '''pq:P459 wd:Q590232.'''
            query += '''
                                                         SERVICE wikibase:label {
                                                            bd:serviceParam wikibase:language "en".
                                                            }
                                                         }
                                                         '''
        elif z in ['0 degree Celsius', '75 degree', 'degree Celsius']:
            query = '''
                                SELECT ?answerLabel WHERE {
                                '''
            query += "wd:{0} p:{1} ?statement.".format(y, x)
            query += '''?statement ps:{0} ?answer;'''.format(x)
            query += '''pq:P2076 ({0}|1).'''.format(int(z.split(" ")[0]))
            query += '''
                                                         SERVICE wikibase:label {
                                                            bd:serviceParam wikibase:language "en".
                                                            }
                                                         }
                                                         '''
        elif z == 'liquid':
            query = '''
                                            SELECT ?answerLabel WHERE {
                                            '''
            query += "wd:{0} p:{1} ?statement.".format(y, x)
            query += '''?statement ps:{0} ?answer;'''.format(x)
            query += '''pq:P515 wd:Q11435.'''
            query += '''
                                                                     SERVICE wikibase:label {
                                                                        bd:serviceParam wikibase:language "en".
                                                                        }
                                                                     }
                                                                     '''
        elif z == 'solid':
            query = '''
                                                        SELECT ?answerLabel WHERE {
                                                        '''
            query += "wd:{0} p:{1} ?statement.".format(y, x)
            query += '''?statement ps:{0} ?answer;'''.format(x)
            query += '''pq:P515 wd:Q11438.'''
            query += '''
                                                                                 SERVICE wikibase:label {
                                                                                    bd:serviceParam wikibase:language "en".
                                                                                    }
                                                                                 }
                                                                                 '''
        elif z == 'DUTCH':
            query = '''
                            SELECT ?answerLabel WHERE {
                            '''
            query += '''
                                 wd:{0} schema:description ?answer.
                                 FILTER(LANG(?answer) = "nl")
                                 '''.format(y)
            query += '''
                             SERVICE wikibase:label {
                                 bd:serviceParam wikibase:language "nl".
                                 }
                             }
                             '''

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
                    if type(x) == list:
                        for xx in x:
                            x_id = get_wiki_id(xx, type="property", x=i)
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
                        if x_id and y_id:
                            query = get_query(x_id, y_id, z)
                            answer = get_answer(query)
                            if z == "COUNT":
                                if answer[0] != "0":  # As 0 is returned if noting is found for the COUNT
                                    return answer
                            elif z in ['sixth', 'seventh', 'third', 'second', 'fourth']:
                                for ans in answer:
                                    for u in range(3):
                                        new_y_id = get_wiki_id(ans, type="entity", x=u)
                                        new_query = get_query(None, new_y_id, None)
                                        new_answer = get_answer(new_query)
                                        try:
                                            if z in new_answer[0]:
                                                returned_ans = list()
                                                returned_ans.append(ans)
                                                return returned_ans
                                        except IndexError:
                                            pass
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

    return None


def main(argv):
    print("# Input a question:")
    for line in sys.stdin:
        line = line.strip().split("\t")
        if len(line) == 2:
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
        else:
            print("Error: Please input question in right format!", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
