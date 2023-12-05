# app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password123@mysql:3306/microdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    biography = db.Column(db.Text)


@app.route('/createPersona', methods=['POST'])
def createPersona():
    data = request.get_json()
    newPersona = Persona(name=data['name'], biography=data['biography'])
    db.session.add(newPersona)
    db.session.commit()
    return jsonify({'message': 'Persona created successfully', 'personaData': data})


@app.route('/getAllPersonas', methods=['GET'])
def getAllPersonas():
    personas = Persona.query.all()
    personaData = [{'id': persona.id, 'name': persona.name, 'biography': persona.biography} for persona in personas]
    return jsonify({'personas': personaData})


@app.route('/getPersona/<name>', methods=['GET'])
def getPersona(name):
    persona = Persona.query.filter_by(name=name).first()
    if persona:
        personaData = {'id': persona.id, 'name': persona.name, 'biography': persona.biography}
        return jsonify({'persona': personaData})
    else:
        return jsonify({'message': 'Persona not found'}), 404


if __name__ == '__main__':
    # Create the Users table
    with app.app_context():
        db.create_all()

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5001)
