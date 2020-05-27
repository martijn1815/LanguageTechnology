import spacy
import sys
import requests

def search_entitycode(url, entity):
    params = {'action': 'wbsearchentities',
              'language': 'en',
              'format': 'json'}

    params['search'] = entity
    json = requests.get(url, params).json()
    entities = [result['id'] for result in json['search']]

    return entities[0]

def search_propertycode(url, property):
    params = {'action': 'wbsearchentities',
              'language': 'en',
              'format': 'json',
              'type': 'property'}

    params['search'] = property
    json = requests.get(url, params).json()
    properties = [result['id'] for result in json['search']]

    return properties[0]

def create_query(X,Y):
    query = '''
    SELECT ?answer ?answerLabel WHERE {
    wd:''' + Y + ''' wdt:''' + X + ''' ?answer.
    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en" .
    }
    }
    '''
    return query

def run_query(query):
    url = 'https://query.wikidata.org/sparql'

    data = requests.get(url, params={'query': query, 'format': 'json'}).json()
    return data

def main():
    nlp = spacy.load("en_core_web_sm")
    url = 'https://www.wikidata.org/w/api.php'
    for question in sys.stdin:
        property_word = ''
        entity = ''
        doc = nlp(question.rstrip())
        for token in doc:
            print("\t".join((token.text, token.lemma_, token.pos_,
                             token.dep_, token.head.lemma_)))

        #print(entity, property_word)
        #entity_code = search_entitycode(url, entity)
        #property_code = search_propertycode(url, property_word)
        #query = create_query(property_code, entity_code)
        #data = run_query(query)

        #if len(data['results']['bindings']) == 0:
        #    print("Could not find the answer to that question.")
        #else:
        #    for item in data['results']['bindings']:
        #        for var in item:
        #            if var == 'answerLabel':
        #                print('{}'.format(item[var]['value']))

main()