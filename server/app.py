#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
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


# GET /campers
@app.route('/campers', methods=['GET'])
def get_campers():
    campers = Camper.query.all()
    return jsonify([camper.to_dict(only=('id', 'name', 'age')) for camper in campers])


# GET /campers/<int:id>
@app.route('/campers/<int:id>', methods=['GET'])
def get_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    return jsonify(camper.to_dict(only=('id', 'name', 'age', 'signups')))


# POST /campers
@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    try:
        camper = Camper(name=data.get('name'), age=data.get('age'))
        db.session.add(camper)
        db.session.commit()
        return jsonify(camper.to_dict(only=('id', 'name', 'age'))), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400


# PATCH /campers/<int:id>
@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return jsonify({"error": "Camper not found"}), 404
    
    data = request.get_json()
    try:
        if 'name' in data:
            camper.name = data['name']
        if 'age' in data:
            camper.age = data['age']
        db.session.commit()
        return jsonify(camper.to_dict(only=('id', 'name', 'age'))), 202
    except ValueError as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


# GET /activities
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities])


# DELETE /activities/<int:id>
@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    
    db.session.delete(activity)
    db.session.commit()
    return '', 204


# POST /signups
@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    try:
        signup = Signup(
            camper_id=data.get('camper_id'),
            activity_id=data.get('activity_id'),
            time=data.get('time')
        )
        db.session.add(signup)
        db.session.commit()
        return jsonify(signup.to_dict(only=('id', 'camper_id', 'activity_id', 'time', 'camper', 'activity'))), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)

