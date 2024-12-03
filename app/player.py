from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db

player_bp = Blueprint('player', __name__, template_folder="templates")

@player_bp.route('/')
def get_players():
    """Fetches and displays a list of all players."""
    try:
        query = """
        SELECT p.id, p.firstname, p.lastname, c.country, p.position, p.foot, p.height
        FROM player p
        LEFT JOIN countries c ON p.country_id = c.id
        ORDER BY p.lastname, p.firstname;
        """
        players = db.executeQuery(query)
        players = [
            {
                "id": player[0],
                "firstname": player[1],
                "lastname": player[2],
                "country": player[3],
                "position": player[4],
                "foot": player[5],
                "height": player[6],
            }
            for player in players
        ]
    except Exception as e:
        players = []
        print(f"Error fetching players: {e}")
    return render_template('player/index.html', players=players)

@player_bp.route('/<int:id>')
def get_player(id):
    """Fetches and displays details of a single player by ID."""
    try:
        query = """
        SELECT p.firstname, p.lastname, p.birthdate, c.country, p.position, p.foot, p.height
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
        }
    except Exception as e:
        print(f"Error fetching player details: {e}")
        flash("Error fetching player details.", "danger")
        return redirect(url_for('player.get_players'))
    return render_template('player/details.html', player=player)

@player_bp.route('/add', methods=['GET', 'POST'])
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
