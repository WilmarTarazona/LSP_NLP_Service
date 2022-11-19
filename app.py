from flask import Flask, jsonify, request
import spacy

app = Flask(__name__)

try:
    nlp = spacy.load('es_core_news_lg')
except:
    spacy.cli.download('es_core_news_lg')
    nlp = spacy.load('es_core_news_lg')

@app.route('/')
def home():
    return "LSP_NLP_Service"

def find_root_of_sentence(doc):
    root_token = None
    for token in doc:
        if (token.dep_ == "ROOT"):
            root_token = token
    return root_token

def find_other_verbs(doc, root_token):
    other_verbs = []
    for token in doc:
        ancestors = list(token.ancestors)
        if (token.pos_ == "VERB" and len(ancestors) == 1\
            and ancestors[0] == root_token):
            other_verbs.append(token)
    return other_verbs

def get_clause_token_span_for_verb(verb, doc, all_verbs):
    first_token_index = len(doc)
    last_token_index = 0
    this_verb_children = list(verb.children)
    for child in this_verb_children:
        if (child not in all_verbs):
            if (child.i < first_token_index):
                first_token_index = child.i
            if (child.i > last_token_index):
                last_token_index = child.i
    return(first_token_index, last_token_index + 1)

def divide_sentence(sentence):
    doc = nlp(sentence)
    root_token = find_root_of_sentence(doc)
    other_verbs = find_other_verbs(doc, root_token)
    token_spans = []   
    all_verbs = [root_token] + other_verbs
    for other_verb in all_verbs:
        (first_token_index, last_token_index) = \
         get_clause_token_span_for_verb(other_verb, 
                                        doc, all_verbs)
        token_spans.append((first_token_index, 
                            last_token_index))

    sentence_clauses = []
    for token_span in token_spans:
        start = token_span[0]
        end = token_span[1]
        if (start < end):
            clause = doc[start:end]
            sentence_clauses.append(clause)
    sentence_clauses = sorted(sentence_clauses, 
                              key=lambda tup: tup[0])

    clauses_text = [clause.text for clause in sentence_clauses]
    return clauses_text

@app.route('/LSP', methods=['POST'])
def LSP():    
    try:
        sentences = divide_sentence(list(request.json.values())[0])

        
        full = []
        for i in sentences:
            doc = nlp(i)
            lista = []
            hay_verbo = False
            hay_interrogativo = False
            hay_tiempo = False

            verbo = ""
            interrogativo = ""
            tiempo = ""
            for token in doc:
                if token.pos_ != "ADP" and token.pos_ != "AUX" and token.pos_ != "PUNCT":
                    if(token.pos_ == 'NOUN' and token.dep_ == 'obl'):
                        tiempo = token.text
                        hay_tiempo = True
                    elif(token.pos_ == 'VERB' and token.dep_ == 'ROOT'):
                        verbo = token.lemma_
                        hay_verbo = True
                    elif(token.pos_ == 'PRON' and token.dep_ == 'nsubj'):
                        interrogativo = token.text
                        hay_interrogativo = True
                    else:
                        lista.append(token.text)
                if(hay_verbo):
                    lista.append(verbo)
                if(hay_interrogativo):
                    lista.append(interrogativo)
                if(hay_tiempo):
                    lista.insert(0, tiempo)
            full += lista

        return jsonify({'mensaje': full, 'exito': True})
    except:
        return jsonify({'exito': False})

if __name__ == "__main__":
    app.run()