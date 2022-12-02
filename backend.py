import flask
from flask_cors import CORS
from flask.json import jsonify
import uuid
from robotron import Maze


app = flask.Flask(__name__)
CORS(app)

@app.route("/", methods=["POST"])
def create():
    global model
    model = Maze()

    response.port(5000)
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
app.run()