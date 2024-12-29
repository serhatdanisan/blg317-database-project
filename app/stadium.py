from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from auth import isAdmin

MATCHES_QUERY = '''
    SELECT
        fm.id AS matchid,
        fm.dateutc AS time,
        hc.name AS home,
        fm.goal_by_home_club || ':' || fm.goal_by_away_club AS score,
        ac.name AS away,
        hc.id AS home_id,
        ac.id AS away_id,
        fm.competition AS competition
    FROM football_match fm
    JOIN club hc ON hc.id = fm.home_club
    JOIN club ac ON ac.id = fm.away_club
    JOIN stadiums s ON s.id = fm.stadiums_id
    WHERE s.id = %s
    ORDER BY time DESC

'''


stadium_bp = Blueprint('stadium', __name__, template_folder="templates")

@stadium_bp.route('/')
def get_stadiums():
    """Fetches and displays a list of all stadiums with optional filters."""
    try:
        name = request.args.get('name', '').strip()
        city = request.args.get('city', '').strip()
        country_id = request.args.get('country', '').strip()
        capacity_min = request.args.get('capacity_min', '').strip()
        capacity_max = request.args.get('capacity_max', '').strip()

        query = """
        SELECT s.id, s.stadium, s.city, c.country, s.capacity
        FROM stadiums s
        LEFT JOIN countries c ON s.country_id = c.id
        WHERE 1=1
        """
        params = []

        if name:
            query += " AND s.stadium ILIKE %s"
            params.append(f"%{name}%")
        if city:
            query += " AND s.city ILIKE %s"
            params.append(f"%{city}%")
        if country_id:
            query += " AND s.country_id = %s"
            params.append(country_id)
        if capacity_min:
            query += " AND s.capacity >= %s"
            params.append(capacity_min)
        if capacity_max:
            query += " AND s.capacity <= %s"
            params.append(capacity_max)

        query += " ORDER BY s.stadium;"
        stadiums = db.executeQuery(query, params)
        stadiums = [
            {
                "id": row[0],
                "name": row[1],
                "city": row[2],
                "country": row[3],
                "capacity": row[4],
            }
            for row in stadiums
        ]

        unique_names = [row[0] for row in db.executeQuery("SELECT DISTINCT stadium FROM stadiums ORDER BY stadium;")]
        unique_cities = [row[0] for row in db.executeQuery("SELECT DISTINCT city FROM stadiums ORDER BY city;")]
        countries = [{"id": row[0], "name": row[1]} for row in db.executeQuery("SELECT id, country FROM countries ORDER BY country;")]

        return render_template('stadium/index.html', 
                               stadiums=stadiums, 
                               unique_names=unique_names, 
                               unique_cities=unique_cities, 
                               countries=countries, 
                               filters=request.args)
    except Exception as e:
        print(f"Error fetching stadiums: {e}")
        return render_template('stadium/index.html', stadiums=[], unique_names=[], unique_cities=[], countries=[], filters={})


@stadium_bp.route('/<int:id>')
def get_stadium(id):
    """Fetches and displays details of a single stadium by ID."""
    try:
        query = """
        SELECT s.stadium, s.city, c.country, s.capacity, s.confederation, c.id, s.id
        FROM stadiums s
        LEFT JOIN countries c ON s.country_id = c.id
        WHERE s.id = %s;
        """
        stadium_data = db.executeQuery(query, params=(id,))
        
        if not stadium_data:
            return render_template('stadium/details.html', stadium=None, error=f"Stadium with ID {id} not found.")

        stadium = {
            "name": stadium_data[0][0],
            "city": stadium_data[0][1],
            "country": stadium_data[0][2],
            "capacity": stadium_data[0][3],
            "confederation": stadium_data[0][4],
            "country_id": stadium_data[0][5],
            "stadium_id": stadium_data[0][6]
        }


        match_history = db.executeQuery(MATCHES_QUERY, params=(id,))

    except Exception as e:
        stadium = None
        print(f"Error fetching stadium details: {e}")
        return render_template('stadium/details.html', stadium=None, error=str(e))

    return render_template('stadium/details.html', stadium=stadium,
                                                    match_history=match_history,
                                                      error=None)

@stadium_bp.route('/add', methods=['GET', 'POST'])
@isAdmin
def add_stadium():
    """Adds a new stadium."""
    if request.method == 'POST':
        try:
            stadium = request.form['stadium']
            city = request.form['city']
            capacity = int(request.form['capacity'])
            confederation = request.form['confederation']
            country_id= request.form['country_id']

            query = """
            INSERT INTO stadiums (stadium, city, capacity, confederation, country_id)
            VALUES (%s, %s, %s, %s, %s);
            """
            db.executeQuery(query, params=(stadium, city, capacity, confederation, country_id), commit=1)
            flash('Stadium added successfully!', 'success')
            return redirect(url_for('stadium.get_stadiums'))
        except Exception as e:
            print(f"Error adding stadium: {e}")
            flash('Error adding stadium. Please try again.', 'danger')
    countries = db.executeQuery("SELECT id, country FROM countries ORDER BY country;")
    return render_template('stadium/add.html', countries=countries)

@stadium_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@isAdmin
def edit_stadium(id):
    """Edits an existing stadium."""
    if request.method == 'POST':
        try:
            confederation = request.form['confederation']
            stadium = request.form['stadium']
            city = request.form['city']
            capacity = int(request.form['capacity'])
            country_id = request.form['country_id']

            query = """
            UPDATE stadiums
            SET confederation = %s, stadium = %s, city = %s, capacity = %s, country_id = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(confederation, stadium, city, capacity, country_id, id), commit=1)
            flash('Stadium updated successfully!', 'success')
            return redirect(url_for('stadium.get_stadiums'))
        except Exception as e:
            print(f"Error updating stadium: {e}")
            flash('Error updating stadium. Please try again.', 'danger')
    else:
        query = """
        SELECT id, confederation, stadium, city, capacity, country_id
        FROM stadiums
        WHERE id = %s;
        """
        stadium_data = db.executeQuery(query, params=(id,))
        print("Stadium Data:", stadium_data)  # Debugging

        if not stadium_data:
            flash(f"Stadium with ID {id} not found.", 'danger')
            return redirect(url_for('stadium.get_stadiums'))

        stadium = {
            "id": stadium_data[0][0],
            "confederation": stadium_data[0][1],
            "stadium": stadium_data[0][2],
            "city": stadium_data[0][3],
            "capacity": stadium_data[0][4],
            "country_id": stadium_data[0][5],
        }
        countries = db.executeQuery("SELECT id, country FROM countries ORDER BY country;")
        return render_template('stadium/edit.html', stadium=stadium, countries=countries)


@stadium_bp.route('/delete/<int:id>', methods=['POST'])
@isAdmin
def delete_stadium(id):
    """Deletes a stadium."""
    try:
        query = "DELETE FROM stadiums WHERE id = %s;"
        db.executeQuery(query, params=(id,), commit=1)
        flash('Stadium deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting stadium: {e}")
        flash('Error deleting stadium. Please try again.', 'danger')

    return redirect(url_for('stadium.get_stadiums'))
