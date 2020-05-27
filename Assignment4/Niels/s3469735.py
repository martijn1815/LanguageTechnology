import sys
import fileinput
import spacy
import requests
import re
import json


def print_example_queries():
    print("1. When was Uranus discovered?")
    print("2. Who invented the telescope?")
    print("3. When was the Doppler effect discovered")
    print("4. Who invented penicillin")
    print("5. Who was the inventor of penicillin")
    print("6. When was Einstein born?")
    print("7. What are the satellite of Mars?")
    print("8. What was the size of the sun?")
    print("9. What is the heighest point in Italy?")
    print("10. What is the chemical formula of glucose?")


def query(x, y):
    url = "https://www.wikidata.org/w/api.php"
    url2 = "https://query.wikidata.org/sparql"
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    paramsx = {"action": "wbsearchentities", "language":"en", "format":"json", "search":x, "type": "property"}
    paramsy = {"action": "wbsearchentities", "language":"en", "format":"json", "search":y}
    jsonx = requests.get(url, paramsx).json()
    jsony = requests.get(url, paramsy).json()
    hits = {'x': {}, 'y': {}}
    for i in jsonx['search']:
        hits['x'][i['id']] = False
    for i in jsony['search']:
        hits['y'][i['id']] = False
    result_list =[]
    for i in hits['y']:
        for j in hits['x']:
            try:
                q = "SELECT ?a ?aLabel WHERE {wd:"+i+" wdt:"+j+" ?a SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. } }"
                data = requests.get(url2, headers=headers, params={'query': q, 'format': 'json'}).json()
                result_query = []
                for item in data ['results']['bindings']:
                    part = item['a']['value']
                    if 'http://www.wikidata.org/entity' in part:
                        part = item['aLabel']['value']
                    result_query.append(part)
                    hits['x'][j] = True
                    hits['y'][i] = True
                if len(result_query) > 0:
                    result_list.append(result_query)
            except json.decoder.JSONDecodeError:
                None
    print('Results:')
    if len(result_list) == 1:
        st = ', '.join(result_list[0])
        print(st)
    elif len(result_list) == 0:
        print('No results found')
    else:
        ans_list = []
        for i in result_list:
            if i not in ans_list:
                print(i[0])
                ans_list.append(i)


def main():
    print_example_queries()
    nlp = spacy.load('en_core_web_sm')
    print("Please, ask a question")
    for line in fileinput.input():
        firstword = line.split(' ')[0]
        parse = nlp(line)
        n = 0
        xt = []
        yt = []
        x = []
        y = []
        for token in parse:
            func_sent = token.dep_
            if func_sent == 'nsubj':
                xt.append(token.text)
                xpos = 1
            elif func_sent == 'pobj':
                yt.append(token.text)
                ypos = 1
            n += 1
        if xt == ['Who'] or xt == ['who'] or len(xt) == 0:
            for token in parse:
                if token.dep_ == 'attr':
                    xt = [token.text]
        if xt == ['Who'] or xt == ['who'] or (firstword == 'When' and (len(xt) == 0 or len(yt) == 0)):
            for token in parse:
                if token.dep_ == 'ROOT':
                    xt = [token.text]
                elif token.dep_ == 'dobj' or token.dep_ == 'acomp' or token.dep_ == 'compound' or token.dep_ == 'nsubjpass' or token.dep_ =='nsubj':
                    yt = [token.text]
        if xt and yt:
            for token in parse:
                if token.dep_ != 'det' and token.dep_ != 'punct' and token.dep != 'ROOT' and token.dep_ != 'nsubj' and token.dep_ != 'prep' and token.dep_ != 'advmod' and token.dep_ != 'auxpass' and token.dep_ != 'aux':
                    if token.head.text == xt[0] and token.text != yt[0]:
                        xt.append(token.text)
                    elif token.head.text == yt[0] and token.text != xt[0]:
                        yt.append(token.text)
            for token in parse:
                if token.text in xt:
                    x.append(token.text)
                if token.text in yt:
                    y.append(token.text)
            if x[-1] == 'of':
                x.pop()
            x = ' '.join(x)
            y = ' '.join(y)
            query(x,y)
        else:
            print('We could not find any relevant tokens')
        
    print("Program has ended")


if __name__ == "__main__":
    main()

