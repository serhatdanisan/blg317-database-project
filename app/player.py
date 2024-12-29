from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from database import db
import csv
import traceback
from club import GOAL_QUERY
from auth import isAdmin


PLAYER_ASSIST_QUERY = '''
    SELECT
        DISTINCT fme.id AS assists, fme.football_match_id AS match_id
    FROM football_match_event fme
    JOIN player p ON p.id = fme.player_id
    WHERE %s = fme.player_id AND fme.modifier = 'assist'
'''

CLN_SHEET_QUERY = '''

WITH params AS (
    SELECT
        %s AS player_id
),
player_matches AS (
    SELECT DISTINCT fme.football_match_id AS match_id, fme.club_id AS club_id, params.player_id AS player_id
    FROM football_match_event fme, params
    WHERE fme.player_id = params.player_id
)
SELECT *
    FROM football_match fm
    JOIN player_matches pm ON pm.match_id = fm.id
    WHERE (pm.club_id = fm.home_club AND fm.goal_by_away_club = 0) OR
            (pm.club_id = fm.away_club AND fm.goal_by_home_club = 0)

'''

MATCH_QUERY = '''
WITH params AS (
    SELECT
        %s AS player_id
),
player_matches AS (
    SELECT DISTINCT fme.football_match_id AS match_id
    FROM football_match_event fme, params
    WHERE fme.player_id = params.player_id
)
    SELECT
        fm.id AS matchid,
        fm.dateutc AS time,
        hc.name AS home,
        fm.goal_by_home_club || ':' || fm.goal_by_away_club AS score,
        ac.name AS away,
        hc.id AS home_id,
        ac.id AS away_id
    FROM football_match fm
    JOIN player_matches pm ON pm.match_id = fm.id
    JOIN club hc ON hc.id = fm.home_club
    JOIN club ac ON ac.id = fm.away_club
    ORDER BY time DESC


'''



def get_match_count(id):
    matches = db.executeQuery(MATCH_QUERY, params=(id,))
    result = len(matches)
    return result


def get_goal_count(id):

    clubs = db.executeQuery('''SELECT DISTINCT fme.club_id
                                FROM football_match_event fme
                                WHERE fme.player_id = %s 
                            '''
                            , params=(id,))
    total_goals = 0
    for club in clubs:
        club_goals = db.executeQuery(GOAL_QUERY, params=(club,))
        player_goals = [goal for goal in club_goals if goal[1] == id]
        goal_count = len(player_goals)
        total_goals = total_goals + goal_count
    
    return total_goals


def get_assist_count(id):
    assists = db.executeQuery(PLAYER_ASSIST_QUERY, params=(id,))
    result = len(assists)
    return result


def get_cln_sheet_count(id):
    clnsht = db.executeQuery(CLN_SHEET_QUERY, params=(id,))
    result = len(clnsht)
    return result

def load_player_image(player_id):
    player_image = None
    with open('app/static/images/player_images.csv', mode='r') as file:
        for row in csv.DictReader(file):
            dset_id = int(row['dataset_ID'])
            if dset_id == player_id:
                player_image = row['link']
                break
    return player_image


def get_match_goal_count(id, match_id):
        clubs = db.executeQuery('''SELECT DISTINCT fme.club_id
                                    FROM football_match_event fme
                                    WHERE fme.player_id = %s 
                                '''
                                , params=(id,))
        if not clubs:
            return '-'
        
        club = clubs [0][0]
        club_goals = db.executeQuery(GOAL_QUERY, params=(club,))
        player_goals = [goal for goal in club_goals if goal[1] == id and goal[0] == match_id]


        if len(player_goals) == 0:
            return '-'
        else: return len(player_goals)

def get_match_assist_count (id, match_id):
    assists = db.executeQuery(PLAYER_ASSIST_QUERY, params=(id,))
    if not assists:
            return '-'
    assist_count = sum(1 for assist in assists if assist[1] == match_id)

    if assist_count == 0:
            return '-'
    else: return assist_count
 
player_bp = Blueprint('player', __name__, template_folder="templates")


@player_bp.route('/')
def get_players():
    """Fetches and displays a list of all players with optional filters."""
    try:
        firstname = request.args.get('firstname', '').strip()
        lastname = request.args.get('lastname', '').strip()
        country = request.args.get('country', '').strip()
        position = request.args.get('position', '').strip()

        query = """
        SELECT p.id, p.firstname, p.lastname, c.country, p.position
        FROM player p
        LEFT JOIN countries c ON p.country_id = c.id
        WHERE 1=1
        """
        params = []

        if firstname:
            query += " AND p.firstname ILIKE %s"
            params.append(f"%{firstname}%")
        if lastname:
            query += " AND p.lastname ILIKE %s"
            params.append(f"%{lastname}%")
        if country:
            query += " AND c.id = %s"
            params.append(country)
        if position:
            query += " AND p.position = %s"
            params.append(position)

        query += " ORDER BY p.lastname, p.firstname LIMIT 100;"
        players = db.executeQuery(query, params)

        players = [
            {
                "id": player[0],
                "firstname": player[1],
                "lastname": player[2],
                "country": player[3],
                "position": player[4],
            }
            for player in players
        ]

        countries = [{"id": row[0], "name": row[1]} for row in db.executeQuery("SELECT id, country FROM countries ORDER BY country;")]
        positions = [row[0] for row in db.executeQuery("SELECT DISTINCT position FROM player WHERE position IS NOT NULL ORDER BY position;")]

        return render_template('player/index.html', players=players, countries=countries, positions=positions, filters=request.args)

    except Exception as e:
        flash(f"Error fetching players: {str(e)}", "danger")
        return redirect(url_for('player.get_players'))

@player_bp.route('/<int:id>')
def get_player(id):
    """Fetches and displays details of a single player by ID."""
    try:
        query = """
        SELECT p.firstname, p.lastname, p.birthdate, c.country, p.position, p.foot, p.height, c.id, p.id
        FROM player p
        LEFT JOIN countries c ON p.country_id = c.id
        WHERE p.id = %s;
        """
        player_data = db.executeQuery(query, params=(id,))
        if not player_data:
            flash(f"Player with ID {id} not found.", 'danger')
            return redirect(url_for('player.get_players'))

        player = {
            "firstname": player_data[0][0],
            "lastname": player_data[0][1],
            "birthdate": player_data[0][2],
            "country": player_data[0][3],
            "position": player_data[0][4],
            "foot": player_data[0][5],
            "height": player_data[0][6],
            "country_id": player_data[0][7],
            "id": player_data[0][8]
        }

        player_image = load_player_image(id)

        match_count = get_match_count(id)
        player_goal_count = get_goal_count(id)
        player_assist_count = get_assist_count(id)
        cln_sheet_count = get_cln_sheet_count(id)
        match_history = db.executeQuery(MATCH_QUERY, params=(id,))


        print(db.executeQuery(PLAYER_ASSIST_QUERY, params=(id,)))

    except Exception as e:
        print(f"Error fetching player details: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        flash("Error fetching player details.", "danger")
        return redirect(url_for('player.get_players'))
    return render_template('player/details.html', player=player,
                                                match_history=match_history,
                                                match_count=match_count,
                                                player_image=player_image,
                                                player_goal_count=player_goal_count,
                                                player_assist_count=player_assist_count,
                                                cln_sheet_count=cln_sheet_count,
                                                get_match_goal_count=get_match_goal_count,
                                                get_match_assist_count=get_match_assist_count)

@player_bp.route('/add', methods=['GET', 'POST'])
@isAdmin
def add_player():
    """Adds a new player."""
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            birthdate = request.form['birthdate']
            country_id = request.form['country_id'] or None
            position = request.form['position']
            foot = request.form['foot']
            height = request.form['height']

            query = """
            INSERT INTO player (firstname, lastname, birthdate, country_id, position, foot, height)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            db.executeQuery(query, params=(firstname, lastname, birthdate, country_id, position, foot, height), commit=1)
            flash('Player added successfully!', 'success')
            return redirect(url_for('player.get_players'))
        except Exception as e:
            print(f"Error adding player: {e}")
            flash('Error adding player. Please try again.', 'danger')
    # Fetch countries for the dropdown
    countries = db.executeQuery("SELECT id, country FROM countries ORDER BY country;")
    return render_template('player/add.html', countries=countries)

@player_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@isAdmin
def edit_player(id):
    """Edits an existing player."""
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            birthdate = request.form['birthdate']
            country_id = request.form['country_id'] or None
            position = request.form['position']
            foot = request.form['foot']
            height = request.form['height']

            query = """
            UPDATE player
            SET firstname = %s, lastname = %s, birthdate = %s, country_id = %s, position = %s, foot = %s, height = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(firstname, lastname, birthdate, country_id, position, foot, height, id), commit=1)
            flash('Player updated successfully!', 'success')
            return redirect(url_for('player.get_players'))
        except Exception as e:
            print(f"Error updating player: {e}")
            flash('Error updating player. Please try again.', 'danger')
    else:
        # Fetch player details for pre-filling the form
        player_query = "SELECT * FROM player WHERE id = %s;"
        player_data = db.executeQuery(player_query, params=(id,))
        if not player_data:
            flash(f"Player with ID {id} not found.", 'danger')
            return redirect(url_for('player.get_players'))

        player = {
            "id": player_data[0][0],
            "firstname": player_data[0][1],
            "lastname": player_data[0][2],
            "birthdate": player_data[0][3],
            "country_id": player_data[0][4],
            "position": player_data[0][5],
            "foot": player_data[0][6],
            "height": player_data[0][7],
        }
        # Fetch countries for the dropdown
        countries = db.executeQuery("SELECT id, country FROM countries ORDER BY country;")
        return render_template('player/edit.html', player=player, countries=countries)

@player_bp.route('/delete/<int:id>', methods=['POST'])
@isAdmin
def delete_player(id):
    """Deletes a player."""
    try:
        query = "DELETE FROM player WHERE id = %s;"
        db.executeQuery(query, params=(id,), commit=1)
        flash('Player deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting player: {e}")
        flash('Error deleting player. Please try again.', 'danger')
    return redirect(url_for('player.get_players'))
