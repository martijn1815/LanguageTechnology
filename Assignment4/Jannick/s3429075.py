import spacy
import sys
import requests

def search_entitycode(url, entity):
    params = {'action': 'wbsearchentities',
              'language': 'en',
              'format': 'json'}
    try:
        params['search'] = entity
        json = requests.get(url, params).json()
        entities = [result['id'] for result in json['search']]

        return (entities[0], entities[1])
    except KeyError:
        print("The entity could not be found. Check your spelling.")

def search_propertycode(url, property):
    params = {'action': 'wbsearchentities',
              'language': 'en',
              'format': 'json',
              'type': 'property',
              'limit': 20}

    try:
        params['search'] = property
        json = requests.get(url, params).json()
        properties = [result['id'] for result in json['search']]

        try:
            return properties[0]
        except IndexError:
            pass
    except KeyError:
        print("Could not find the answer to that question")

def create_query(X,Y):
    try:
        query = '''
        SELECT ?answer ?answerLabel WHERE {
        wd:''' + Y + ''' wdt:''' + X + ''' ?answer.
        SERVICE wikibase:label {
            bd:serviceParam wikibase:language "en" .
        }
        }
        '''
        return query
    except TypeError:
        print("Something went wrong in the creation of the query. Try again.")

def run_query(query):
    url = 'https://query.wikidata.org/sparql'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like GecKo) Chrome/51.0.2704.103 Safari/537.36'
    }

    data = requests.get(url, headers= headers, params={'query': query, 'format': 'json'}).json()
    return data

def get_synonyms(property_word, og_entity, url):
    synonym_dict = {'invent': ['designed', 'inventor'],
                    'found': 'founder',
                    'design': 'designed',
                    'inventors': 'inventor'}
    try:
        new_properties = synonym_dict[property_word]
        synonym_query(new_properties, og_entity, url)
    except KeyError:
        print("Could not find the answer to that question")

def synonym_query(property_words, og_entity, url):
    if len(property_words) == 0:
        print("Could not find the answer to that question")
    else:
        new_property = property_words[0]
        new_property_code = search_propertycode(url, new_property)
        query = create_query(new_property_code, og_entity)
        data = run_query(query)
        if len(data['results']['bindings']) == 0:
            synonym_query(property_words[1:], og_entity, url)
        else:
            for item in data['results']['bindings']:
                for var in item:
                    if var == 'answerLabel':
                        print('{}'.format(item[var]['value']))

def main():
    nlp = spacy.load("en_core_web_sm")
    url = 'https://www.wikidata.org/w/api.php'

    print("What are the parts of a plant?\n"
          "What is the highest point of Italy?\n"
          "Who invented penicillin?\n"
          "What is opposite to a black hole?\n"
          "Who is the inventor of the automobile?\n"
          "Who wrote the Leviathan?\n"
          "Which parts make up a neuron?\n"
          "What is the atomic number of silver?\n"
          "What is the chemical formula of the water?\n"
          "What moons does Mars have?")

    print("")
    print("Ask question to the system.\n"
          "Press CTRL + D to terminate the program.")

    quick_translation_dict = {'moons': 'child astronomical body',
                              'formula': 'defining formula'}

    for question in sys.stdin:
        property_word = ''
        entity = ''
        doc = nlp(question.rstrip())
        for token in doc:
            if token.dep_ == 'nsubj':
                if property_word == '' and token.pos_ != 'PRON' and token.text not in entity:
                    property_word = token.text
                elif entity == '' and token.pos_ != 'PRON' and token.text not in property_word:
                    entity = token.text
            elif token.dep_ in ['pobj', 'dobj']:
                if property_word == '':
                    property_word = token.text
                elif entity == '':
                    entity = token.text
            elif token.dep_ == 'attr':
                if property_word == '' and token.pos_ != 'PRON':
                    property_word = token.text
            elif token.dep_ == 'compound':
                if token.head.dep_ == 'nsubj':
                    property_word = "{} {}".format(token.text, token.head)
                elif token.head.dep_ == 'pobj':
                    entity = "{} {}".format(token.text, token.head)
                elif token.head.dep_ == 'ROOT':
                    entity = token.text
            elif token.pos_ == 'ADJ':
                if property_word == '' and token.head.dep_ == 'nsubj':
                    property_word = "{} {}".format(token.text, token.head)
                elif entity == '' and token.head.dep_ in ['pobj', 'dobj']:
                    entity = "{} {}".format(token.text, token.head)
                else:
                    if property_word == '':
                        property_word = token.text
            elif token.pos_ == 'VERB':
                if property_word == '':
                    property_word = token.lemma_
            elif token.pos_ == 'NOUN':
                if property_word == '' and token.head.dep_ == 'nsubj':
                    property_word = "{} {}".format(token.text, token.head)
                elif entity == '':
                    entity = token.text
                else:
                    property_word = token.text

        try:
            property_word = quick_translation_dict[property_word]
        except KeyError:
            property_word = property_word

        entity_codes = search_entitycode(url, entity)
        property_code = search_propertycode(url, property_word)
        query = create_query(property_code, entity_codes[0])
        data = run_query(query)

        if len(data['results']['bindings']) == 0:
            new_entity = entity_codes[1]
            new_query = create_query(property_code, new_entity)
            new_data = run_query(new_query)
            if len(new_data['results']['bindings']) == 0:
                get_synonyms(property_word, entity_codes[0], url)
            else:
                for item in new_data['results']['bindings']:
                    for var in item:
                        if var == 'answerLabel':
                            print('{}'.format(item[var]['value']))
        else:
            for item in data['results']['bindings']:
                for var in item:
                    if var == 'answerLabel':
                        print('{}'.format(item[var]['value']))

main()