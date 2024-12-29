from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth import isAdmin
from database import db
from collections import Counter
import csv


country_bp = Blueprint('country', __name__, template_folder="templates")


def load_player_images(players):
    all_ids = {p[0] for p in (players)}
    player_data = {}
    with open('app/static/images/player_images.csv', mode='r') as file:
        for row in csv.DictReader(file):
            dset_id = int(row['dataset_ID'])
            if dset_id in all_ids:
                player_data[dset_id] = row['link']
    return player_data


GOAL_QUERY = '''
WITH params AS (
    SELECT 
        %s AS country_id
),
country_players AS (
    SELECT 
        p.id AS player_id
    FROM player p, params
    WHERE p.country_id = params.country_id
),
filtered_events AS (
    SELECT 
        e.id AS event_id, 
        e.club_id, 
        e.player_id,
        e.matchperiod, 
        e.eventsec, 
        e.action,
        e.football_match_id
    FROM football_match_event e
    WHERE 
        e.eventname = 'Save attempt'
        AND e.is_success = FALSE
),
goal_details AS (
    SELECT 
        e.id AS event_id,
        e.player_id,
        e.club_id,
        e.matchperiod,
        e.eventsec,
        e.football_match_id,
        CASE 
            WHEN e.action = 'Penalty' THEN TRUE
            ELSE FALSE
        END AS is_penalty
    FROM football_match_event e
    JOIN filtered_events fe ON e.id = fe.event_id - 1
    WHERE e.football_match_id = fe.football_match_id
),
country_goals AS (
    SELECT 
        gd.football_match_id AS match_id,
        gd.player_id,
        gd.club_id,
        gd.matchperiod,
        gd.eventsec,
        gd.is_penalty
    FROM goal_details gd
    JOIN country_players cp ON gd.player_id = cp.player_id
)
SELECT 
    cg.player_id,
    p.firstname || ' ' || p.lastname AS player_name
FROM country_goals cg
JOIN player p ON cg.player_id = p.id
ORDER BY cg.match_id, cg.eventsec;
'''

ASSIST_QUERY = '''
    SELECT
        p.id AS playerid,
        p.firstname || ' ' || p.lastname AS player_name
    FROM football_match_event fme
    JOIN player p ON p.id = fme.player_id
    JOIN club c ON c.id = fme.club_id
    WHERE p.country_id = %s AND fme.modifier = 'assist'

'''



def get_top_scorers(id):
   
    goals = db.executeQuery(GOAL_QUERY, params=(id,))
    player_count = Counter(goal[0] for goal in goals)  # goal[0] = player_id

    # En çok yazılan ilk 5 player_id'yi ve tekrar sayılarını alıyoruz
    top_5 = player_count.most_common(5)

    # player_id -> player_name eşlemesini bulmak için bir dict oluşturuyoruz
    player_names = {goal[0]: goal[1] for goal in goals}  # goal[2] = player_name

    # İlk 5 oyuncunun id ve ismini alıp döndürüyoruz
    result = [(player_id, player_names[player_id], count) for player_id, count in top_5]
    return result

def get_top_assists(id):
   
    assists = db.executeQuery(ASSIST_QUERY, params=(id,))
    player_count = Counter(assist[0] for assist in assists)  # assist[0] = player_id

    # En çok yazılan ilk 5 player_id'yi ve tekrar sayılarını alıyoruz
    top_5 = player_count.most_common(5)

    # player_id -> player_name eşlemesini bulmak için bir dict oluşturuyoruz
    player_names = {assist[0]: assist[1] for assist in assists}  # assist[3] = player_name

    # İlk 5 oyuncunun id ve ismini alıp döndürüyoruz
    result = [(player_id, player_names[player_id], count) for player_id, count in top_5]
    return result

def get_top_contributions(goal_list, assist_list):

    # Sözlük kullanarak oyuncuları id ile takip edelim
    contributions = {}

    # Gol katkılarını ekleyelim
    for player_id, player_name, goals in goal_list:
        if player_id not in contributions:
            contributions[player_id] = {
                "player_name": player_name,
                "goals": goals,
                "assists": 0,
            }
        else:
            contributions[player_id]["goals"] += goals

    # Asist katkılarını ekleyelim
    for player_id, player_name, assists in assist_list:
        if player_id not in contributions:
            contributions[player_id] = {
                "player_name": player_name,
                "goals": 0,
                "assists": assists,
            }
        else:
            contributions[player_id]["assists"] += assists

    # Toplam katkıyı hesapla ve listeye dönüştür
    combined_list = [
        (
            player_id,
            details["player_name"],
            details["goals"] + details["assists"],
        )
        for player_id, details in contributions.items()
    ]

    # Toplam katkıya göre azalan sırada sırala
    combined_list.sort(key=lambda x: x[2], reverse=True)

    # İlk 5 oyuncuyu döndür
    return combined_list[:5]



@country_bp.route('/')
def get_countries():
    """Fetches and displays a list of all countries."""
    try:
        name = request.args.get('name', '').strip()
        capital_city = request.args.get('capital_city', '').strip()
        region = request.args.get('region', '').strip()
        
        query = """
        SELECT id, country, capital_city, region
        FROM countries
        WHERE 1=1
        """
        params = []

        if name:
            query += " AND country = %s"
            params.append(name)
        if capital_city:
            query += " AND capital_city = %s"
            params.append(capital_city)
        if region:
            query += " AND region = %s"
            params.append(region)

        query += " ORDER BY country;"
        countries = db.executeQuery(query, params)
        countries = [
            {
                "id": country[0],
                "name": country[1],
                "capital_city": country[2],
                "region": country[3],
            }
            for country in countries
        ]

        unique_names = [row[0] for row in db.executeQuery("SELECT DISTINCT country FROM countries ORDER BY country;")]
        unique_capitals = [row[0] for row in db.executeQuery("SELECT DISTINCT capital_city FROM countries ORDER BY capital_city;")]
        unique_regions = [row[0] for row in db.executeQuery("SELECT DISTINCT region FROM countries ORDER BY region;")]

    except Exception as e:
        countries = []
        print(f"Error fetching countries: {e}")

    return render_template('country/index.html', countries=countries, unique_names=unique_names, unique_regions=unique_regions, unique_capitals=unique_capitals, filters=request.args)

@country_bp.route('/<int:id>')
def get_country(id):
    """Fetches and displays details of a single country by ID."""
    try:
        query = """
        SELECT *
        FROM countries
        WHERE id = %s;
        """
        country_data = db.executeQuery(query, params=(id,))
        if not country_data:
            flash(f"Country with ID {id} not found.", 'danger')
            return redirect(url_for('country.get_countries'))

        country = {
            "id":country_data[0][0],
            "name": country_data[0][1],
            "capital_city": country_data[0][2],
            "region": country_data[0][3],
        }
        top_scorers = get_top_scorers(id)
        scorer_player_images = load_player_images(top_scorers)

        top_assists = get_top_assists(id)
        assist_player_images = load_player_images(top_assists)

        top_contributions = get_top_contributions(top_scorers, top_assists)
        cont_player_images = load_player_images(top_contributions)

        print(top_scorers)
    except Exception as e:
        print(f"Error fetching country details: {e}")
        flash("Error fetching country details.", "danger")
        return redirect(url_for('country.get_countries'))
    return render_template('country/details.html', country=country,                            
                           top_scorers=top_scorers,
                           top_assists=top_assists, 
                           top_contributions=top_contributions,
                           scorer_player_images=scorer_player_images,
                           assist_player_images=assist_player_images,
                           cont_player_images=cont_player_images)

@country_bp.route('/add', methods=['GET', 'POST'])
@isAdmin
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
@isAdmin
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
@isAdmin
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
