#!/usr/bin/env python3
import sys
import requests
import spacy


def print_examples():
    examples = ['What is the orbital inclination of the ISS?', 'Apple Inc. was founded by who?', 
                'Who are the crew members of the Apollo 11?', 'Who invented the World Wide Web?',
                'What does blood consist of?', 'What parts does a plant have?',
                'Give the chemical formula of glucose','Who discovered penicillin?',
                'Which shapes does DNA have?','Symptoms of ADD?']
    for example in examples:
        print(example)


def analyse(parse):
    prop_lst = []
    ent_lst = []
    pos_tags = []
    for token in parse:
        pos_tags.append(token.pos_)

    if 'VERB' in pos_tags[1:]: #if question contains a verb but does not begin with a verb
        for token in parse:
            if token.dep_ == 'ROOT': #usually the property
                if parse[0].dep_ == 'pobj' or parse[0].dep_ == 'advmod':
                    prop_lst.append(token.lemma_)

                else: #likely that a date will be returned if person neede so change verb to noun
                    if token.lemma_[-1] == 't':
                        noun = token.lemma_ + 'or'
                        prop_lst.append(noun)
                    elif token.lemma_[-1] == 'e':
                        noun = token.lemma_[:-1] + 'or'
                        prop_lst.append(noun)
                    elif token.lemma_[-1] == 'r' or token.lemma_[-1] == 'd':
                        noun = token.lemma_ + 'er'
                        prop_lst.append(noun)
                    else:
                        prop_lst.append(token.lemma_)

            if token.dep_ in ['dobj','nsubj','nsubjpass'] and token.pos_ != 'PRON': #usually the entity
                for tok in token.subtree:
                    if tok.dep_ != 'det':
                        ent_lst.append(tok.text)

    if 'VERB' not in pos_tags: #if question does not contain a verb
        if pos_tags.count('AUX') == 1:
            for token in parse:
                if (token.dep_ == 'nsubj' or token.dep_ == 'attr') and token.pos_ != 'PRON': #usually the property
                    for tok in token.subtree:
                        if tok.dep_ != 'det' and tok.dep_ != 'prep':
                            if tok.head.text == token.text or tok.text == token.text: #check if head of tok is token
                                prop_lst.append(tok.lemma_)

                if token.dep_ == 'pobj': #usually the entity
                    for tok in token.subtree:
                        if tok.dep_ != 'det':
                            ent_lst.append(tok.text)
        
        if pos_tags.count('AUX') > 1:
            for token in parse:
                if token.dep_ == 'dobj': #if more aux in sentence this usually property
                    for tok in token.subtree:
                        if tok.dep_ != 'det':
                            prop_lst.append(tok.lemma_)

                if token.dep_ == 'nsubj': #if more aux in sentence this usually entity
                    for tok in token.subtree:
                        if tok.dep_ != 'det':
                            ent_lst.append(tok.text)

        else:
            for token in parse:
                if token.dep_ == 'ROOT' and token.pos_ == 'NOUN': #if no aux usually property
                    for tok in token.subtree:
                        if tok.dep_ == 'compound' or tok.dep_ == 'ROOT':
                            if tok.head.text == token.text or tok.text == token.text: #check if head of tok is token
                                prop_lst.append(tok.lemma_)

                if token.dep_ == 'pobj': #if no aux usually entity
                    for tok in token.subtree:
                        if tok.dep_ != 'det':
                            ent_lst.append(tok.text)

    if 'VERB' == pos_tags[0]: #if question starts with a verb
        for token in parse:
            if token.dep_ == 'dobj': #usually property
                for tok in token.subtree:
                    if tok.dep_ != 'det' and tok.dep_ != 'prep':
                        if tok.head.text == token.text or tok.text == token.text: #check if head of tok is token
                            prop_lst.append(tok.lemma_)

            if token.dep_ == 'pobj': #usually entity
                for tok in token.subtree:
                    if tok.dep_ != 'det':
                        ent_lst.append(tok.lemma_)


    prop = []
    [prop.append(item) for item in prop_lst if item not in prop] #remove duplicate words
    ent = [] 
    [ent.append(item) for item in ent_lst if item not in ent] #remove duplicate words

    return ' '.join(prop), ' '.join(ent)


def get_property(prop):
    wdt = []
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action':'wbsearchentities',
              'type':'property',
              'language':'en',
              'format':'json'}

    params['search'] = prop
    json = requests.get(url,params).json()
    if len(json['search']) == 0: #if there is no result
        params['search'] = prop[0:-1] #search prop without last char (example -s)
        json = requests.get(url,params).json()
        for result in json['search']:
            wdt.append(result['id'])
    else:
        for result in json['search']:
            wdt.append(result['id'])

    return wdt


def get_entity(ent):
    wd = []
    url = 'https://www.wikidata.org/w/api.php'
    params = {'action':'wbsearchentities',
              'language':'en',
              'format':'json'}

    params['search'] = ent
    json = requests.get(url,params).json()
    for result in json['search']:
        wd.append(result['id'])

    return wd


def create_query(X,Y):
    query = '''
    SELECT ?answer ?answerLabel WHERE{
    wd:''' + Y + ''' wdt:''' + X + ''' ?answer.
    SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en" .
    }
    }'''
    return query

def run_query(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    }
    url = 'https://query.wikidata.org/sparql'
    data = requests.get(url, headers=headers, params={'query' : query, 'format':'json'}).json()
    answers = []
    for item in data['results']['bindings']:
        answers.append(item['answerLabel']['value'])

    return answers


def main(argv):
    print_examples()
    nlp = spacy.load('en_core_web_sm')

    for question in sys.stdin:
        parse = nlp(question.strip())

        prop, ent = analyse(parse)

        if len(prop) == 0 or len(ent) == 0:
            print('Could not find an answer to this question')
      
        else:
            possible_answers = []
            Xlist = get_property(prop)
            Ylist = get_entity(ent)

            for Y in Ylist:
                for X in Xlist:
                    q = create_query(X,Y)
                    a = run_query(q)
                    if len(a) != 0:
                        possible_answers.append(a)
            if len(possible_answers) == 0:
                print('Could not find an answer to this question')
            else:
                likely_answer = possible_answers[0]
                print(', '.join(likely_answer))


if __name__ == "__main__":
    main(sys.argv)