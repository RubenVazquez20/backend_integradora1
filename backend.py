import flask
from flask_cors import CORS
from flask.json import jsonify
import json
import uuid
import os
from robotron import Maze


app = flask.Flask(__name__)
CORS(app)

port = int(os.getenv('PORT, 8000'))

@app.rout('/')
def root():
    return jsonify (
        [
            {
                "message" : "funcionando :)"
            }
        ]
    )

@app.route("/", methods=["POST"])
def create():
    global model
    model = Maze()

    response = jsonify("ok")
    response.status_code = 201
    response.headers['Access-Control-Expose-Headers'] = '*'
    response.autocorrect_location_header = False
    return response

@app.route("/step", methods=["GET"])
def queryState():
    model.step()
    cajas = model.getCajas()
    stack = model.getStack()
    chiquitos = model.getChiquitos()
    muros = model.getMuros()
    depositos = model.getDepositos()
    return jsonify({"stack": stack,"cajas":cajas, "chiquitos": chiquitos, "muros": muros, "depositos":depositos})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= port, debug=True)