from flask import Flask, jsonify, request
from flasgger import Swagger
from contamehistorias.datasources.webarchive import ArquivoPT
from datetime import datetime
from contamehistorias import engine
import json

try:
    import simplejson as json
except ImportError:
    import json
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus

def res(intervals, verbose=False):
    n_docs = 0
    n_domains = 0
    output="nothing"
    date=[]
    article=[]
    i=-1
    if (intervals):
        output="Timeline"+"\n"
        if("results" in intervals.keys()):
          periods = intervals["results"]
          for period in periods:
            i=i+1
            date.append(str(period["from"])+" until "+str(period["to"]))
            output+=str(period["from"])+" until "+str(period["to"])+"\n"        
            keyphrases = period["keyphrases"]
            article.append([])
            for keyphrase in keyphrases:
                if(verbose):            
                    output+=str(keyphrase.headlines[0].info.datetime.date())+"["+str(keyphrase.headlines[0].info.domain)+"]"+str(keyphrase.kw)+"\n"
                    article[i].append(str(keyphrase.headlines[0].info.datetime.date())+"["+str(keyphrase.headlines[0].info.domain)+"]"+str(keyphrase.kw))
                else:           
                    output+=str(keyphrase.kw)+"\n"
                    article[i].append(str(keyphrase.kw))
        n_domains = len(intervals["domains"])
        n_docs = intervals["stats"]["n_docs"]
        output+="Summary"+"\n"+"Number of unique domains "+str(n_domains)+"\n"+"Found documents "+str(n_docs)
    return [output,[date,article]]



app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Conta me historias API Explorer',
    'uiversion': 3
}
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_pampo',
            "route": '/flasgger_static/apispec_conta.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
swagger = Swagger(app,config=swagger_config)

@swagger.validate('content')
@app.route('/conta',methods=['POST'])
def handle_conta():
    """Conta me Historias
    ---
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
        - name: content
          in: body
          description: content object
          required: true
          schema:
            $ref: '#/definitions/content'
    requestBody:
        description: Optional description in *Markdown*
        required: true
        content:
          application/json:
            schema:
              id: content
              type: object
    responses:
      200:
        description: Extract NamedEntities from input text
        schema:
            $ref: '#/definitions/result'
    definitions:
      content:
        description: content object
        properties:
          query:
            type: string
          domains:
            type: array
            items: string
          start_date:
            type: string
          end_date:
            type: string
        required:
          - query
          - domains
          - start_date
          - end_date
        example:   # Sample object
            query: Dilma Roussef
            domains : [ 'http://publico.pt/', 'http://www.rtp.pt/','http://www.dn.pt/', 'http://news.google.pt/']
            start_date: "2016-07-21 17:32:28"
            end_date: "2018-07-21 17:32:28"
      result:
        type: object
        properties:
            domains:
              type: array
              items: string
            results:
              type: array
              items: object
            stats:
              type: object
              properties:
                  n_unique_docs:
                    type: integer
                  n_docs:
                    type: integer
                  n_domains:
                    type: integer
                  time:
                    type: integer
    """
    try:
        assert request.json["domains"] , "Invalid domains"
        assert request.json["query"] , "Invalid query"
        assert request.json["start_date"] , "Invalid start_date"
        assert request.json["end_date"] , "Invalid end_date"
        domains = request.json["domains"]
        start_date = datetime.strptime(request.json["start_date"], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(request.json["end_date"], '%Y-%m-%d %H:%M:%S')
        query = request.json["query"]

        params = {'domains':domains,'from':start_date,'to':end_date}
        apt =  ArquivoPT()
        search_result = apt.getResult(query=query, **params)
        language = "pt"
  
        cont = engine.TemporalSummarizationEngine()
        intervals = cont.build_intervals(search_result, language)
        result  = res(intervals)

        return jsonify(result), HTTPStatus.OK

    except Exception as e:
        return jsonify(str(e)), HTTPStatus.BAD_REQUEST

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8004)
