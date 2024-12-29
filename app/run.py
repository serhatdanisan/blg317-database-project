from flask import Flask, render_template
from home import home_bp
from player import player_bp
from stadium import stadium_bp
from country import country_bp
from club import club_bp
from event import event_bp
from match import match_bp
from stats_page import match_details_bp
from auth import auth_bp
from search import search_bp
from database import db


def create_app():
    app = Flask('Football', template_folder='app/templates', static_folder='app/static')  # Ana templates dizini
    app.secret_key = 'EECY'
    
    # Blueprint'leri uygulamaya kaydediyoruz
    app.register_blueprint(home_bp, url_prefix='/')  # home blueprint kaydedildi
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(stadium_bp, url_prefix='/stadium')
    app.register_blueprint(country_bp, url_prefix='/country')
    app.register_blueprint(club_bp, url_prefix='/club')
    app.register_blueprint(match_bp, url_prefix='/match')
    app.register_blueprint(event_bp, url_prefix='/event')  
    app.register_blueprint(match_details_bp)
    app.register_blueprint(auth_bp) 
    app.register_blueprint(search_bp) 

    @app.route('/')
    def home():
        return render_template("base.html")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
