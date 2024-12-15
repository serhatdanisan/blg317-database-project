from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db

country_bp = Blueprint('country', __name__, template_folder="templates")

@country_bp.route('/')
def get_countries():
    """Fetches and displays a list of all countries."""
    try:
        query = """
        SELECT id, country, capital_city, region
        FROM countries
        ORDER BY country;
        """
        countries = db.executeQuery(query)
        countries = [
            {
                "id": country[0],
                "name": country[1],
                "capital_city": country[2],
                "region": country[3],
            }
            for country in countries
        ]
    except Exception as e:
        countries = []
        print(f"Error fetching countries: {e}")
    return render_template('country/index.html', countries=countries)

@country_bp.route('/<int:id>')
def get_country(id):
    """Fetches and displays details of a single country by ID."""
    try:
        query = """
        SELECT country, capital_city, region
        FROM countries
        WHERE id = %s;
        """
        country_data = db.executeQuery(query, params=(id,))
        if not country_data:
            flash(f"Country with ID {id} not found.", 'danger')
            return redirect(url_for('country.get_countries'))

        country = {
            "name": country_data[0][0],
            "capital_city": country_data[0][1],
            "region": country_data[0][2],
        }
    except Exception as e:
        print(f"Error fetching country details: {e}")
        flash("Error fetching country details.", "danger")
        return redirect(url_for('country.get_countries'))
    return render_template('country/details.html', country=country)

@country_bp.route('/add', methods=['GET', 'POST'])
def add_country():
    """Adds a new country."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            capital_city = request.form['capital_city']
            region = request.form['region']

            query = """
            INSERT INTO countries (country, capital_city, region)
            VALUES (%s, %s, %s);
            """
            db.executeQuery(query, params=(name, capital_city, region), commit=1)
            flash('Country added successfully!', 'success')
            return redirect(url_for('country.get_countries'))
        except Exception as e:
            print(f"Error adding country: {e}")
            flash('Error adding country. Please try again.', 'danger')
    return render_template('country/add.html')

@country_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_country(id):
    """Edits an existing country."""
    if request.method == 'POST':
        try:
            name = request.form['name']
            capital_city = request.form['capital_city']
            region = request.form['region']

            query = """
            UPDATE countries
            SET country = %s, capital_city = %s, region = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(name, capital_city, region, id), commit=1)
            flash('Country updated successfully!', 'success')
            return redirect(url_for('country.get_countries'))
        except Exception as e:
            print(f"Error updating country: {e}")
            flash('Error updating country. Please try again.', 'danger')
    else:
        country_query = "SELECT * FROM countries WHERE id = %s;"
        country_data = db.executeQuery(country_query, params=(id,))
        if not country_data:
            flash(f"Country with ID {id} not found.", 'danger')
            return redirect(url_for('country.get_countries'))

        country = {
            "id": country_data[0][0],
            "name": country_data[0][1],
            "capital_city": country_data[0][2],
            "region": country_data[0][3],
        }
        return render_template('country/edit.html', country=country)

@country_bp.route('/delete/<int:id>', methods=['POST'])
def delete_country(id):
    """Deletes a country."""
    try:
        query = "DELETE FROM countries WHERE id = %s;"
        db.executeQuery(query, params=(id,), commit=1)
        flash('Country deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting country: {e}")
        flash('Error deleting country. Please try again.', 'danger')
    return redirect(url_for('country.get_countries'))
