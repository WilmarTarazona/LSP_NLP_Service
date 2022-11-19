from flask import Flask, jsonify, request
import spacy

app = Flask(__name__)

try:
    nlp = spacy.load('es_core_news_sm')
except:
    spacy.cli.download('es_core_news_sm')
    nlp = spacy.load('es_core_news_sm')

@app.route('/')
def home():
    return "LSP_NLP_Service"

@app.route('/LSP', methods=['POST'])
def LSP():    
    try:
        doc = nlp(list(request.json.values())[0])
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
                    # verbo = pattern.es.conjugate(str(verbo), pattern.es.INFINITIVE)
                    hay_verbo = True
                elif(token.pos_ == 'PRON' and token.dep_ == 'nsubj'):
                    interrogativo = token.text
                    hay_interrogativo = True
                else:
                    lista.append(token.text)
        if(hay_verbo):
            # verbo = pattern.es.conjugate(str(verbo), pattern.es.INFINITIVE)
            lista.append(verbo)
        if(hay_interrogativo):
            lista.append(interrogativo)
        if(hay_tiempo):
            lista.insert(0, tiempo)
        return jsonify({'mensaje': lista, 'exito': True})
    except:
        return jsonify({'exito': True})

if __name__ == "__main__":
    app.run()