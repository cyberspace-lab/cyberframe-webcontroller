from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import func
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

cors = CORS(app, origins="*")

class Position(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=func.now())

    def json(self):
        return {'id': self.id, 'x': self.x, 'y': self.y, 'timestamp': self.timestamp}

db.create_all()

# get latest position by timestamp
@app.route('/positions/latest', methods=['GET'])
def get_latest_position():
    try:
        latest_position = Position.query.order_by(desc(Position.timestamp)).first()
        if latest_position:
            return make_response(jsonify({'position': latest_position.json()}), 200)
        else:
          default_position = {'x': 0, 'y': 0}
          return make_response(jsonify({'position': default_position, 'message': 'No positions found'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting position: {str(e)}'}), 500)
    
# create a position
@app.route('/positions', methods=['POST'])
def create_position():
    try:
        data = request.get_json()
        new_position = Position(x=data['x'], y=data['y'])
        db.session.add(new_position)
        db.session.commit()
        return make_response(jsonify({'message': 'Position created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': 'Error creating position: ' + str(e)}), 500)
    
# get all positions
@app.route('/positions', methods=['GET'])
def get_positions():
  try:
    positions = Position.query.order_by(desc(Position.timestamp)).all()
    return make_response(jsonify([position.json() for position in positions]), 200)
  except e:
    return make_response(jsonify({'message': 'error getting positions'}), 500)

# get top x positions
@app.route('/positions/<int:topX>', methods=['GET'])
def get_top_x_positions(topX):
  try:
    positions = Position.query.order_by(desc(Position.timestamp)).limit(topX).all()
    return make_response(jsonify([position.json() for position in positions]), 200)
  except e:
    return make_response(jsonify({'message': f'error getting top {str(topX)} positions'}), 500)
  
# delete all positions
@app.route('/positions/delete', methods=['DELETE'])
def delete_all_positions():
    try:
        db.session.query(Position).delete()
        db.session.commit()
        return make_response(jsonify({'message': 'All positions deleted'}), 200)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'message': 'Error deleting positions: ' + str(e)}), 500)

# create a test route
@app.route('/test', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)