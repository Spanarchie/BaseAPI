#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, make_response, make_response, request, current_app
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from datetime import timedelta
from functools import update_wrapper
from py2neo import Graph

graph = Graph("http://PyBase:sZzmKcoKKjG1pnUhjitl@pybase.sb04.stations.graphenedb.com:24789/db/data/")
app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/')
def hello_world():
    return 'Hello crule World!'

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

person_fields = {
        'userName': fields.String,
        'playerID': fields.String,
        'firstName': fields.String,
        'lastName': fields.String,
        'city':fields.String,
        'email': fields.String,
        'bankRef': fields.String,
        'gender':fields.String,
        'role': fields.String,
        'active': fields.String,
        'img': fields.String
    }


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return {'tasks': [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201


class PeopleListAPI(Resource):
    # decorators = [auth.login_required]
    people = []

    def __init__(self):
        super(PeopleListAPI, self).__init__()


    @crossdomain(origin='*')
    def get(self):
        if self.people == []:
            qry = "MATCH (n :PERSON)  RETURN n"
            ans = graph.cypher.execute(qry)
            for x in ans:
                person = {
                    'userName': x[0]['userName'],
                    'playerID': x[0]['playerID'],
                    'firstName': x[0]['firstName'],
                    'lastName': x[0]['lastName'],
                    'city': x[0]['city'],
                    'email': x[0]['email'],
                    'bankRef': x[0]['bankRef'],
                    'gender':x[0]['gender'],
                    'role': x[0]['role'],
                    'active': x[0]['active'],
                    'img': x[0]['img']
                }
                self.people.append(person)
        return jsonify({'people': self.people})



class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': True}


api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(PeopleListAPI, '/todo/api/v1.0/people', endpoint='people')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')


if __name__ == '__main__':
    app.run(debug=True)