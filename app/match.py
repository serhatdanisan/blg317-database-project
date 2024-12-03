from flask import Blueprint

match_bp = Blueprint('match', __name__)

@match_bp.route('/')
def get_matches():
    return "List of matches"

@match_bp.route('/<int:id>')
def get_match(id):
    return f"Details of match {id}"
