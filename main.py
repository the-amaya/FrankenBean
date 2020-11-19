from flask import Flask
from flask_restful import Api, Resource, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import markdown
import os, sys
from flask_cors import CORS, cross_origin
import subprocess

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beanapi.db?cache=shared'
db = SQLAlchemy(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
binpath = sys.executable

onHardware = 0

# the land of functions

def dbupdate(name, state):
	print(name, state)
	dbi = coilModel.query.filter_by(name=name).first()
	dbi.state = state
	db.session.commit()


def dbcheck(name):
	dbi = coilModel.query.filter_by(name=name).first()
	print(dbi.state)
	return dbi.state


class coilModel(db.Model):
	__tablename__ = 'coilModel'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	state = db.Column(db.Integer, nullable=False)
	def __repr__(self):
		return f"coil(id = {id}, name = {name}, state = {state})"


@app.after_request
def gnu_terry_pratchett(resp):
	resp.headers.extend({'X-Clacks-Overhead': 'GNU Terry Pratchett'})
	print("this fucking thing is not working")
	return resp


@app.route("/")
def index():
	"""Present some documentation"""
	# Open the README file
	with open(os.path.dirname(app.instance_path) + '/README.md', 'r') as markdown_file:

		# Read the content of the file
		content = markdown_file.read()
		# Convert to HTML
		return markdown.markdown(content), 200


resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'state': fields.Integer
}


class state(Resource):
	@marshal_with(resource_fields)
	def get(self, name):
		if name == "all":
			result = coilModel.query.all()
			return result, 202
		else:
			result = coilModel.query.filter_by(name=name).first()
			if not result:
				abort(404, message="input or output name not found")
			return result, 202


class command(Resource):
	def post(self, command_a):
		if command_a == "brew":
			#TODO check if we are already brewing before calling the brew process again
			if (dbcheck('active') == 1):
				return 'unable to start brewing at this time, another brew is already in progress, check back later', 503
			if onHardware:
				dbupdate('active', 1)
				p = subprocess.Popen([binpath, "brew.py"])
				return 'brew cycle starting', 202
			else:
				dbupdate('active', 1)
				p = subprocess.Popen([binpath, "test.py"])
				return 'we are currently running in dev mode, started the test script', 202

def db_create():
	#todo add a check to see if the database already exists, either here or in the main loop when we call this
	db.drop_all()
	db.create_all()
	#todo add brew start time, current system time, brew completed time
	states = [
		['pump', '0'],
		['w_solenoid', '0'],
		['heat', '0'],
		['vent', '0'],
		['air_pump', '0'],
		['fill_low', '0'],
		['fill_med', '0'],
		['fill_high', '0'],
		['overfill', '0'],
		['flow', '0'],
		['temperature', '0'],
		['active', '0'],
		['start_time', '0'],
		['current_time', '0'],
		['end_time', '0']
	]
	c = 1
	for i in states:
		ins = coilModel(id=c, name=i[0], state=int(i[1]))
		db.session.add(ins)
		c = c++1
	print('database created and initialized')
	db.session.commit()


api.add_resource(state, "/state/<string:name>")
api.add_resource(command, "/command/<string:command_a>")

if __name__ == "__main__":
	db_create()
	#todo add a database update/reset function here
	app.run(host='0.0.0.0',debug=True)
