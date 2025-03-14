from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, ObjectType, QueryType, MutationType
from ariadne.constants import PLAYGROUND_HTML

app = Flask(__name__, static_folder='build')
CORS(app)

schema = make_executable_schema(type_defs, query, mutation)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200
type_defs = ""
query = ObjectType("Query")
mutation = ObjectType("Mutation")

schema = make_executable_schema(type_defs, query, mutation)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
