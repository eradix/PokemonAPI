from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# DB connection
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://lebron:1234@localhost:3306/pokedex' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define model

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False)
    pokemons = db.relationship('Pokemon', backref='type', lazy=True)

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)


# Define routes

# INDEX 
@app.route('/api/v2/pokemons', methods=['GET'])
def get_pokemons():
    pokemons = Pokemon.query.all()
    if pokemons:
        result = [
                {
                    'id': pokemon.id, 
                    'name': pokemon.name, 
                    'description': pokemon.description, 
                    'type': pokemon.type.type_name
                }
                  for pokemon in pokemons
            ]
    else:
        result = {
            'message': 'No pokemon available as of now.'
        }

    return jsonify(result)


# SHOW
@app.route('/api/v2/pokemon/<int:pokemon_id>', methods=['GET'])
def get_pokemon(pokemon_id):
    pokemon = Pokemon.query.session.get(Pokemon, pokemon_id)
    if pokemon:
        result = {
            'id': pokemon.id,
            'name': pokemon.name, 
            'description': pokemon.description, 
            'type_id': pokemon.type_id, 
            'type': pokemon.type.type_name
        }
        return jsonify(result)
    else:
        return jsonify(
                {'message': 'Item not found'}
            ), 404


# STORE
@app.route('/api/v2/pokemons', methods=['POST'])
def create_pokemon():
    data = request.get_json()
    new_pokemon = Pokemon(name=data['name'], description=data.get('description', ''), type_id=data['type_id'])
    db.session.add(new_pokemon)
    db.session.commit()
    return jsonify({'message': f'Pokemon {data["name"]} created successfully'}), 201


# UPDATE
@app.route('/api/v2/pokemon/<int:pokemon_id>', methods=['PUT'])
def update_pokemon(pokemon_id):
    pokemon = Pokemon.query.session.get(Pokemon, pokemon_id)
    if pokemon:
        data = request.get_json()
        pokemon.name = data['name']
        pokemon.description = data.get('description', '')
        pokemon.type_id = data['type_id']
        db.session.commit()
        return jsonify({'message': f'Pokemon with id: {pokemon.id} updated successfully'})
    else:
        return jsonify({'message': 'Pokemon not found'}), 404
    

# DELETE
@app.route('/api/v2/pokemon/<int:pokemon_id>', methods=['DELETE'])
def delete_pokemon(pokemon_id):
    pokemon = Pokemon.query.session.get(Pokemon, pokemon_id)
    if pokemon:
        db.session.delete(pokemon)
        db.session.commit()
        return jsonify({'message': f'{pokemon.name} deleted successfully'})
    else:
        return jsonify({'message': 'Pokemon not found'}), 404


# run app
if __name__ == '__main__':
    app.run(debug=True)
