from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aloha123@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'aloha1234'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:8080")

class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:aloha123@localhost/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'aloha1234'
    app.app_context().push()
    db.init_app(app)
    socketio = SocketIO(app, cors_allowed_origins="http://localhost:8080")
    return app

def check_database_changes():
    with app.app_context():
        data = Test.query.all()
        socketio.emit('update_data', {'data': [{'id': item.id, 'name': item.name} for item in data]}, namespace='/')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    data = Test.query.all()
    emit('update_data', {'data': [{'id': item.id, 'name': item.name} for item in data]})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    scheduler = BackgroundScheduler()
    scheduler.add_job(check_database_changes, 'interval', seconds=1)
    scheduler.start()

    socketio.run(app, debug=True)

