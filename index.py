import json

from flask import Flask, request
from flask.templating import render_template
from flask.wrappers import Response

from utils import Client

HASURA_URL = "https://unbiased-rabbit-96.hasura.app/v1/graphql"
HASURA_HEADERS = {"X-Hasura-Admin-Secret": "5qEITb9AYwnOvLvxobVquKwStq7DK3fualHam6xEZ46zm03R433EIuzqbKwinXGJ"}

client = Client(url=HASURA_URL, headers=HASURA_HEADERS)

app = Flask(__name__)


@app.route('/api/keywords', methods=['GET'])
def keywords():
    keywords_response = client.get_keywords()
    data = keywords_response.get('data').get('keyword')
    keywords_list = list()

    if data:
        for keyword in data:
            keywords_list.append(keyword['keyword_value'])

    keywords_list = list(set(keywords_list))

    return Response(json.dumps(keywords_list), mimetype='application/json')


@app.route('/', methods=['GET', 'POST'])
def pairs():
    text_field = request.form.get('text')
    keywords_field = request.form.get('keywords')
    search_field = request.form.get('search')

    if request.method == 'POST':
        if search_field:
            search_field = json.loads(search_field)
            keywords = []
            for item in search_field:
                keywords.append(item.get('value'))

            pairs_response = client.get_pairs_by_keywords(keywords)
            if pairs_response.get("errors"):
                return {"message": pairs_response["errors"][0]["message"]}, 400

            data = pairs_response.get('data').get('text_keyword')
            found = list()

            if data:
                for pair in data:
                    keyword_list = []
                    pair = pair.get("text")
                    text_value = pair.get("text_value")
                    for keyword in pair["text_keywords"]:
                        keyword_list.append(keyword["keyword"]["keyword_value"])

                    found.append({
                        'text': text_value,
                        'keywords': keyword_list
                    })
            print(found)

        if text_field and keywords_field:
            keywords_field = json.loads(keywords_field)

            text_keywords_dict = {
                'data': []
            }

            keywords = []
            for item in keywords_field:
                keywords.append(item.get('value'))

            for k in keywords:
                text_keywords_dict['data'].append({
                    'keyword': {
                        'data': {
                            'keyword_value': k
                        }
                    }
                })

            d = {
                'input': {
                    'text_value': '',
                    'text_keywords': {}
                }
            }

            d['input']['text_value'] = text_field
            d['input']['text_keywords'] = text_keywords_dict

            pair_response = client.create_pair(text_field, text_keywords_dict)
            if pair_response.get("errors"):
                return {"message": pair_response["errors"][0]["message"]}, 400

    pairs_response = client.get_pairs()

    data = pairs_response.get('data').get('text')
    pairs_list = list()

    if data:
        for pair in data:
            keyword_list = []
            text_value = pair.get("text_value")
            for keyword in pair["text_keywords"]:
                keyword_list.append(keyword["keyword"]["keyword_value"])

            pairs_list.append({
                'text': text_value,
                'keywords': keyword_list
            })
    print(pairs_list)

    return render_template('pairs.html', pairs=pairs_list, found=found if search_field else None)


if __name__ == '__main__':
    app.run(debug=True)
