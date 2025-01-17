from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from auth import isAdmin

match_bp = Blueprint('match', __name__, template_folder="templates")

@match_bp.route('/')
@match_bp.route('/')
def get_matches():
    """Fetches and displays a list of all matches with optional filters."""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        competition = request.args.get('competition')
        season = request.args.get('season')
        home_club = request.args.get('home_club')
        away_club = request.args.get('away_club')
        winner = request.args.get('winner')

        query = """
        SELECT m.id, m.dateutc, m.competition, m.season, s.stadium, hc.name AS home_club, ac.name AS away_club, 
               w.name AS winner, m.goal_by_home_club, m.goal_by_away_club
        FROM football_match m
        LEFT JOIN stadiums s ON m.stadiums_id = s.id
        LEFT JOIN club hc ON m.home_club = hc.id
        LEFT JOIN club ac ON m.away_club = ac.id
        LEFT JOIN club w ON m.winner = w.id
        WHERE 1=1
        """
        params = []

        if date_from:
            query += " AND m.dateutc >= %s"
            params.append(date_from)
        if date_to:
            query += " AND m.dateutc <= %s"
            params.append(date_to)
        if competition:
            query += " AND m.competition = %s"
            params.append(competition)
        if season:
            query += " AND m.season = %s"
            params.append(season)
        if home_club:
            query += " AND m.home_club = %s"
            params.append(home_club)
        if away_club:
            query += " AND m.away_club = %s"
            params.append(away_club)
        if winner:
            query += " AND m.winner = %s"
            params.append(winner)

        query += " ORDER BY m.dateutc DESC LIMIT 100;"
        matches = db.executeQuery(query, params)

        matches = [
            {
                "id": match[0],
                "dateutc": match[1],
                "competition": match[2],
                "season": match[3],
                "stadium": match[4],
                "home_club": match[5],
                "away_club": match[6],
                "winner": match[7],
                "goal_by_home_club": match[8],
                "goal_by_away_club": match[9],
            }
            for match in matches
        ]

        clubs = [{"id": row[0], "name": row[1]} for row in db.executeQuery("SELECT id, name FROM club ORDER BY name;")]
        competitions = [row[0] for row in db.executeQuery("SELECT DISTINCT competition FROM football_match ORDER BY competition;")]

        return render_template('match/index.html', matches=matches, clubs=clubs, competitions=competitions, filters=request.args)

    except Exception as e:
        flash(f"Error fetching matches: {str(e)}", "danger")
        return redirect(url_for('match.get_matches'))
'''
@match_bp.route('<int:id>')
def get_match(id):
    try:
        query = """
        SELECT m.dateutc, m.competition, m.season, s.stadium, hc.name AS home_club, ac.name AS away_club, 
               w.name AS winner, m.goal_by_home_club, m.goal_by_away_club
        FROM football_match m
        LEFT JOIN stadiums s ON m.stadiums_id = s.id
        LEFT JOIN club hc ON m.home_club = hc.id
        LEFT JOIN club ac ON m.away_club = ac.id
        LEFT JOIN club w ON m.winner = w.id
        WHERE m.id = %s;
        """
        match_data = db.executeQuery(query, params=(id,))
        if not match_data:
            flash(f"Match with ID {id} not found.", 'danger')
            return redirect(url_for('match.get_matches'))

        match = {
            "dateutc": match_data[0][0],
            "competition": match_data[0][1],
            "season": match_data[0][2],
            "stadium": match_data[0][3],
            "home_club": match_data[0][4],
            "away_club": match_data[0][5],
            "winner": match_data[0][6],
            "goal_by_home_club": match_data[0][7],
            "goal_by_away_club": match_data[0][8],
        }
    except Exception as e:
        flash("Error fetching match details.", "danger")
        return redirect(url_for('match.get_matches'))
    return render_template('match/details.html', match=match)
'''
@match_bp.route('/add', methods=['GET', 'POST'])
@isAdmin
def add_match():
    """Adds a new match."""
    if request.method == 'POST':
        try:
            dateutc = request.form['dateutc']
            competition = request.form['competition']
            season = request.form['season']
            stadiums_id = request.form['stadiums_id']
            home_club = request.form['home_club']
            away_club = request.form['away_club']
            winner = request.form['winner'] or None
            goal_by_home_club = request.form['goal_by_home_club']
            goal_by_away_club = request.form['goal_by_away_club']

            query = """
            INSERT INTO football_match (dateutc, competition, season, stadiums_id, home_club, away_club, winner, goal_by_home_club, goal_by_away_club)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            db.executeQuery(query, params=(dateutc, competition, season, stadiums_id, home_club, away_club, winner, goal_by_home_club, goal_by_away_club), commit=1)
            flash('Match added successfully!', 'success')
            return redirect(url_for('match.get_matches'))
        except Exception as e:
            print(f"Error adding match: {e}")
            flash('Error adding match. Please try again.', 'danger')

    stadiums = db.executeQuery("SELECT id, stadium FROM stadiums ORDER BY stadium;")
    clubs = db.executeQuery("SELECT id, name FROM club ORDER BY name;")
    return render_template('match/add.html', stadiums=stadiums, clubs=clubs)

@match_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@isAdmin
def edit_match(id):
    """Edits an existing match."""
    if request.method == 'POST':
        try:
            dateutc = request.form['dateutc']
            competition = request.form['competition']
            season = request.form['season']
            stadiums_id = request.form['stadiums_id']
            home_club = request.form['home_club']
            away_club = request.form['away_club']
            winner = request.form['winner'] or None
            goal_by_home_club = request.form['goal_by_home_club']
            goal_by_away_club = request.form['goal_by_away_club']

            query = """
            UPDATE football_match
            SET dateutc = %s, competition = %s, season = %s, stadiums_id = %s, home_club = %s, away_club = %s, winner = %s, goal_by_home_club = %s, goal_by_away_club = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(dateutc, competition, season, stadiums_id, home_club, away_club, winner, goal_by_home_club, goal_by_away_club, id), commit=1)
            flash('Match updated successfully!', 'success')
            return redirect(url_for('match.get_matches'))
        except Exception as e:
            print(f"Error updating match: {e}")
            flash('Error updating match. Please try again.', 'danger')
    else:
        match_query = "SELECT * FROM football_match WHERE id = %s;"
        match_data = db.executeQuery(match_query, params=(id,))
        if not match_data:
            flash(f"Match with ID {id} not found.", 'danger')
            return redirect(url_for('match.get_matches'))

        match = {
            "id": match_data[0][0],
            "dateutc": match_data[0][1],
            "competition": match_data[0][2],
            "season": match_data[0][3],
            "stadiums_id": match_data[0][4],
            "home_club": match_data[0][5],
            "away_club": match_data[0][6],
            "winner": match_data[0][7],
            "goal_by_home_club": match_data[0][8],
            "goal_by_away_club": match_data[0][9],
        }
        stadiums = db.executeQuery("SELECT id, stadium FROM stadiums ORDER BY stadium;")
        clubs = db.executeQuery("SELECT id, name FROM club ORDER BY name;")
        return render_template('match/edit.html', match=match, stadiums=stadiums, clubs=clubs)

@match_bp.route('/delete/<int:id>', methods=['POST'])
@isAdmin
def delete_match(id):
    """Deletes a match."""
    try:
        query = "DELETE FROM football_match WHERE id = %s;"
        db.executeQuery(query, params=(id,), commit=1)
        flash('Match deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting match: {e}")
        flash('Error deleting match. Please try again.', 'danger')
    return redirect(url_for('match.get_matches'))
