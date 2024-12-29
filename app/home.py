from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from stats_page import match_details

home_bp = Blueprint('home', __name__, template_folder="templates")

@home_bp.route('/')
def get_matches():
    """Fetches and displays the latest 5 matches on the home page."""
    try:
        query = """
        SELECT m.id, m.dateutc, m.competition, hc.id AS home_club_id, hc.name AS home_club, 
               ac.id AS away_club_id, ac.name AS away_club, 
               m.goal_by_home_club, m.goal_by_away_club
        FROM football_match m
        LEFT JOIN club hc ON m.home_club = hc.id
        LEFT JOIN club ac ON m.away_club = ac.id
        ORDER BY m.dateutc DESC
        LIMIT 5;
        """
        matches = db.executeQuery(query)
        matches = [
            {
                "id": match[0],
                "dateutc": match[1],
                "competition": match[2],
                "home_club_id": match[3],
                "home_club": match[4],
                "away_club_id": match[5],
                "away_club": match[6],
                "goal_by_home_club": match[7],
                "goal_by_away_club": match[8],
            }
            for match in matches
        ]
    except Exception as e:
        matches = []
        print(f"Error fetching matches for home page: {e}")
    return render_template("home/index.html", matches=matches)

@home_bp.route('/match/<int:id>')
def get_match(id):
    return match_details(id)

