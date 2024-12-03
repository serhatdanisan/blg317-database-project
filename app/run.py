from flask import Flask
from player import player_bp
from stadium import stadium_bp
from match import match_bp
from country import country_bp
from database import db

def create_app():
    app = Flask('Football', template_folder='templates', static_folder='static')
    app.secret_key = 'EECY'
    
    # Blueprint'leri uygulamaya kaydediyoruz
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(stadium_bp, url_prefix='/stadium')
    app.register_blueprint(match_bp, url_prefix='/match')
    app.register_blueprint(country_bp, url_prefix='/country')
    
    # Default route ekliyoruz
    @app.route('/')
    def home():
        return "Welcome to the Football API!"
    
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
