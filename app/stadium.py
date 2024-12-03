from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db

stadium_bp = Blueprint('stadium', __name__, template_folder="templates")

@stadium_bp.route('/')
def get_stadiums():
    """Fetches and displays a list of all stadiums."""
    try:
        query = """
        SELECT s.id, s.stadium, s.city, c.country, s.capacity
        FROM stadiums s
        LEFT JOIN countries c ON s.country_id = c.id
        ORDER BY s.stadium;
        """
        stadiums = db.executeQuery(query)
        stadiums = [
            {
                "id": stadium[0],
                "name": stadium[1],
                "city": stadium[2],
                "country": stadium[3],
                "capacity": stadium[4],
            }
            for stadium in stadiums
        ]
    except Exception as e:
        stadiums = []
        print(f"Error fetching stadiums: {e}")
    return render_template('stadium/index.html', stadiums=stadiums)

@stadium_bp.route('/<int:id>')
def get_stadium(id):
    """Fetches and displays details of a single stadium by ID."""
    try:
        query = """
        SELECT s.stadium, s.city, c.country, s.capacity, s.confederation
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
        }
    except Exception as e:
        stadium = None
        print(f"Error fetching stadium details: {e}")
        return render_template('stadium/details.html', stadium=None, error=str(e))

    return render_template('stadium/details.html', stadium=stadium, error=None)

@stadium_bp.route('/add', methods=['GET', 'POST'])
def add_stadium():
    """Adds a new stadium."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            city = request.form['city']
            capacity = int(request.form['capacity'])
            confederation = request.form['confederation']

            query = """
            INSERT INTO stadiums (stadium, city, capacity, confederation)
            VALUES (%s, %s, %s, %s);
            """
            db.executeQuery(query, params=(name, city, capacity, confederation), commit=1)
            flash('Stadium added successfully!', 'success')
            return redirect(url_for('stadium.get_stadiums'))
        except Exception as e:
            print(f"Error adding stadium: {e}")
            flash('Error adding stadium. Please try again.', 'danger')
    return render_template('stadium/add.html')

@stadium_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_stadium(id):
    """Edits an existing stadium."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            city = request.form['city']
            capacity = int(request.form['capacity'])
            confederation = request.form['confederation']

            query = """
            UPDATE stadiums
            SET stadium = %s, city = %s, capacity = %s, confederation = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(name, city, capacity, confederation, id), commit=1)
            flash('Stadium updated successfully!', 'success')
            return redirect(url_for('stadium.get_stadiums'))
        except Exception as e:
            print(f"Error updating stadium: {e}")
            flash('Error updating stadium. Please try again.', 'danger')
    else:
        # Fetch stadium details for pre-filling the form
        query = """
        SELECT id, stadium, city, capacity, confederation
        FROM stadiums
        WHERE id = %s;
        """
        stadium_data = db.executeQuery(query, params=(id,))
        if not stadium_data:
            flash(f"Stadium with ID {id} not found.", 'danger')
            return redirect(url_for('stadium.get_stadiums'))

        stadium = {
            "id": stadium_data[0][0],
            "name": stadium_data[0][1],
            "city": stadium_data[0][2],
            "capacity": stadium_data[0][3],
            "confederation": stadium_data[0][4],
        }
        return render_template('stadium/edit.html', stadium=stadium)

@stadium_bp.route('/delete/<int:id>', methods=['POST'])
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
