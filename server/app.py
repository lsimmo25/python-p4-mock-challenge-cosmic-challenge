#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
def get_scientists():

    if request.method == 'GET':
        scientists = [scientist.to_dict() for scientist in Scientist.query.all()]
        return make_response(jsonify(scientists), 200)
    
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        field_of_study = data['field_of_study']

        try:
            new_scientist = Scientist(name=name, field_of_study=field_of_study)
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(jsonify(new_scientist.to_dict()), 200)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)

@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_scientist(id):
    scientist = Scientist.query.filter_by(id=id).first()

    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    if request.method == 'GET':
            scientist_dict = scientist.to_dict(rules=('-missions.scientist', 'missions'))
            return make_response(jsonify(scientist_dict), 200)
        
    if request.method == 'PATCH':
        data = request.get_json()

        try:
            scientist.name = data['name']
            scientist.field_of_study = data['field_of_study']
            db.session.commit()
            return make_response(jsonify(scientist.to_dict(rules=('-missions.scientist', 'missions'))), 202)
        except ValueError as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)


    if request.method == 'DELETE':
        try:
            db.session.delete(scientist)
            db.session.commit()
            return make_response(jsonify({}), 204)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 500)

@app.route('/planets')
def get_planets():
    planets = [planet.to_dict() for planet in Planet.query.all()]
    return make_response(jsonify(planets), 200)

@app.route('/missions', methods=['GET', 'POST'])
def handle_missions():

    missions = [mission.to_dict() for mission in Mission.query.all()]

    if request.method == 'GET':
        return make_response(jsonify(planets), 200)

    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        scientist_id = data['scientist_id']
        planet_id = data['planet_id']

        try:
            new_mission = Mission(name=name, scientist_id=scientist_id, planet_id=planet_id)
            db.session.add(new_mission)
            db.session.commit()
            return make_response(jsonify(new_mission.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
