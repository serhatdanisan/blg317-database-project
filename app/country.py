from flask import Blueprint

country_bp = Blueprint('country', __name__)

@country_bp.route('/')
def get_countries():
    return "List of countries"

@country_bp.route('/<int:id>')
def get_country(id):
    return f"Details of country {id}"
