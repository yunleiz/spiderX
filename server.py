import engine

from flask_cors import CORS
from flask import Flask, Response, json, request

app = Flask(__name__)
CORS(app)


@app.route('/status')
def status():
    return "Works!"


@app.route('/magic', methods=['POST'])
def magic():
    req_data = request.get_json()
    img_path = req_data['path']
    event = {"image": img_path}
    return engine.lambda_handler(event, None)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
