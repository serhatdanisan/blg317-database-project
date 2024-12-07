from flask import Blueprint

club_bp = Blueprint('club', __name__)

@club_bp.route('/')
def get_clubs():
    return "List of clubs"

@club_bp.route('/<int:id>')
def get_club(id):
    return f"Details of club {id}"
