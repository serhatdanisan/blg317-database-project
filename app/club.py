from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db

club_bp = Blueprint('club', __name__, template_folder="templates")

@club_bp.route('/')
def get_clubs():
    try:
        query = """
        SELECT c.id, c.name, c.officialname, c.country, s.stadium
        FROM club c
        LEFT JOIN stadiums s ON c.stadiums_id = s.id
        ORDER BY c.name;

        """
        clubs = db.executeQuery(query)
        clubs = [
            {
                "id": club[0],
                "name": club[1],
                "officialname": club[2],
                "country": club[3],
                "stadium": club[4],
            }
            for club in clubs
        ]
    except Exception as e:
        clubs = []
        print(f"Error fetching clubs: {e}")
    return render_template('club/index.html', clubs=clubs)

@club_bp.route('/<int:id>')
def get_club(id):
    """Fetches and displays details of a single club by ID."""
    try:
        query = """
        SELECT c.name, c.officialname, c.country, s.stadium
        FROM club c
        LEFT JOIN stadiums s ON c.stadiums_id = s.id
        WHERE c.id = %s;
        """
        club_data = db.executeQuery(query, params=(id,))
        if not club_data:
            flash(f"Club with ID {id} not found.", 'danger')
            return redirect(url_for('club.get_clubs'))

        club = {
            "name": club_data[0][0],
            "officialname": club_data[0][1],
            "country": club_data[0][2],
            "stadium": club_data[0][3],
        }
    except Exception as e:
        print(f"Error fetching club details: {e}")
        flash("Error fetching club details.", "danger")
        return redirect(url_for('club.get_clubs'))
    return render_template('club/details.html', club=club)

@club_bp.route('/add', methods=['GET', 'POST'])
def add_club():
    """Adds a new club."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            officialname = request.form['officialname']
            country = request.form['country']
            stadiums_id = request.form['stadiums_id']

            query = """
            INSERT INTO club (name, officialname, country, stadiums_id)
            VALUES (%s, %s, %s, %s);
            """
            db.executeQuery(query, params=(name, officialname, country, stadiums_id), commit=1)
            flash('Club added successfully!', 'success')
            return redirect(url_for('club.get_clubs'))
        except Exception as e:
            print(f"Error adding club: {e}")
            flash('Error adding club. Please try again.', 'danger')

    countries = db.executeQuery("SELECT id, country FROM countries ORDER BY country;")
    stadiums = db.executeQuery("SELECT id, stadium FROM stadiums ORDER BY stadium;")
    return render_template('club/add.html', countries=countries, stadiums=stadiums)

@club_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_club(id):
    """Edits an existing club."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            officialname = request.form['officialname']
            country = request.form['country']
            stadiums_id = request.form['stadiums_id']

            query = """
            UPDATE club
            SET name = %s, officialname = %s, country = %s, stadiums_id = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(name, officialname, country, stadiums_id, id), commit=1)
            flash('Club updated successfully!', 'success')
            return redirect(url_for('club.get_clubs'))
        except Exception as e:
            print(f"Error updating club: {e}")
            flash('Error updating club. Please try again.', 'danger')
    else:
        club_query = "SELECT * FROM club WHERE id = %s;"
        club_data = db.executeQuery(club_query, params=(id,))
        if not club_data:
            flash(f"Club with ID {id} not found.", 'danger')
            return redirect(url_for('club.get_clubs'))

        club = {
            "id": club_data[0][0],
            "name": club_data[0][1],
            "officialname": club_data[0][2],
            "country": club_data[0][3],
            "stadiums_id": club_data[0][4],
        }
        countries = db.executeQuery("SELECT id, country FROM countries ORDER BY country;")
        stadiums = db.executeQuery("SELECT id, stadium FROM stadiums ORDER BY stadium;")
        return render_template('club/edit.html', club=club, countries=countries, stadiums=stadiums)

@club_bp.route('/delete/<int:id>', methods=['POST'])
def delete_club(id):
    """Deletes a club."""
    try:
        query = "DELETE FROM club WHERE id = %s;"
        db.executeQuery(query, params=(id,), commit=1)
        flash('Club deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting club: {e}")
        flash('Error deleting club. Please try again.', 'danger')
    return redirect(url_for('club.get_clubs'))