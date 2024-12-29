from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Flask
from database import db
from auth import isAdmin
import traceback
import csv
import os
from collections import Counter

club_bp = Blueprint('club', __name__, template_folder="templates")

app = Flask(__name__)  # Flask uygulaması

def load_player_images(players):
    all_ids = {p[0] for p in (players)}
    player_data = {}
    with open('app/static/images/player_images.csv', mode='r') as file:
        for row in csv.DictReader(file):
            dset_id = int(row['dataset_ID'])
            if dset_id in all_ids:
                player_data[dset_id] = row['link']
    return player_data

# Oyuncu resimlerini yükle


GOAL_QUERY = '''
WITH params AS (
    SELECT 
        %s AS club_id
),
club_matches AS (
    SELECT 
        fm.id AS match_id,
        CASE 
            WHEN fm.home_club = params.club_id THEN 0 
            WHEN fm.away_club = params.club_id THEN 1 
        END AS team_type
    FROM football_match fm, params
    WHERE fm.home_club = params.club_id OR fm.away_club = params.club_id
),
filtered_events AS (
    SELECT 
        e.id AS event_id, 
        e.club_id, 
        e.player_id,
        e.matchperiod, 
        e.eventsec, 
        e.action,
        e.football_match_id,
        CASE 
            WHEN cm.team_type = 0 THEN fm.home_club
            WHEN cm.team_type = 1 THEN fm.away_club
        END AS team_id
    FROM football_match_event e
    JOIN club_matches cm ON e.football_match_id = cm.match_id
    JOIN football_match fm ON e.football_match_id = fm.id
    WHERE 
        e.eventname = 'Save attempt'
        AND e.is_success = FALSE
        AND e.club_id = CASE 
            WHEN cm.team_type = 0 THEN fm.away_club
            WHEN cm.team_type = 1 THEN fm.home_club
        END
),
goal_details AS (
    SELECT 
        e.id AS event_id,
        e.player_id,
        e.club_id,
        e.matchperiod,
        e.eventsec,
        fe.team_id,
        e.football_match_id,
        CASE 
            WHEN e.action = 'Penalty' THEN TRUE
            ELSE FALSE
        END AS is_penalty
    FROM football_match_event e
    JOIN filtered_events fe ON e.id = fe.event_id - 1
    WHERE e.football_match_id = fe.football_match_id
)
SELECT 
    gd.football_match_id AS match_id,
    gd.player_id,
    p.firstname || ' ' || p.lastname AS player_name,
    p.country_id AS player_country_id,
    gd.matchperiod,
    gd.eventsec,
    CASE 
        WHEN gd.club_id = gd.team_id THEN FALSE
        ELSE TRUE
    END AS is_own_goal,
    gd.is_penalty
FROM goal_details gd
JOIN player p ON gd.player_id = p.id
ORDER BY gd.football_match_id, gd.eventsec;
'''

ASSIST_QUERY = '''
    SELECT
        p.id AS playerid,
        fme.club_id AS club,
        c.name AS clubname,
        p.firstname || ' ' || p.lastname AS player_name,
        p.country_id AS player_country_id
    FROM football_match_event fme
    JOIN player p ON p.id = fme.player_id
    JOIN club c ON c.id = fme.club_id
    WHERE c.id = %s AND fme.modifier = 'assist'

'''

MATCHES_QUERY = '''
    SELECT
        fm.id AS matchid,
        fm.dateutc AS time,
        hc.name AS home,
        fm.goal_by_home_club || ':' || fm.goal_by_away_club AS score,
        ac.name AS away,
        hc.id AS home_id,
        ac.id AS away_id
    FROM football_match fm
    JOIN club hc ON hc.id = fm.home_club
    JOIN club ac ON ac.id = fm.away_club
    WHERE hc.id = %s OR ac.id = %s
    ORDER BY time DESC

'''


def get_top_scorers(id):
   
    goals = db.executeQuery(GOAL_QUERY, params=(id,))
    player_count = Counter(goal[1] for goal in goals)  # goal[1] = player_id

    # En çok yazılan ilk 5 player_id'yi ve tekrar sayılarını alıyoruz
    top_5 = player_count.most_common(5)

    # player_id -> player_name eşlemesini bulmak için bir dict oluşturuyoruz
    player_names = {goal[1]: goal[2] for goal in goals}  # goal[2] = player_name
    player_countries = {goal[1]: goal[3] for goal in goals}  # goal[5] = country_id

    # İlk 5 oyuncunun id ve ismini alıp döndürüyoruz
    result = [(player_id, player_names[player_id], count, player_countries[player_id]) for player_id, count in top_5]
    return result

def get_top_assists(id):
   
    assists = db.executeQuery(ASSIST_QUERY, params=(id,))
    player_count = Counter(assist[0] for assist in assists)  # assist[0] = player_id

    # En çok yazılan ilk 5 player_id'yi ve tekrar sayılarını alıyoruz
    top_5 = player_count.most_common(5)

    # player_id -> player_name eşlemesini bulmak için bir dict oluşturuyoruz
    player_names = {assist[0]: assist[3] for assist in assists}  # assist[3] = player_name
    player_countries = {assist[0]: assist[4] for assist in assists}  # assist[4] = country_id

    # İlk 5 oyuncunun id ve ismini alıp döndürüyoruz
    result = [(player_id, player_names[player_id], count, player_countries[player_id]) for player_id, count in top_5]
    return result

def get_top_contributions(goal_list, assist_list):

    # Sözlük kullanarak oyuncuları id ile takip edelim
    contributions = {}

    # Gol katkılarını ekleyelim
    for player_id, player_name, goals, player_country in goal_list:
        if player_id not in contributions:
            contributions[player_id] = {
                "player_name": player_name,
                "player_country": player_country,
                "goals": goals,
                "assists": 0,
            }
        else:
            contributions[player_id]["goals"] += goals

    # Asist katkılarını ekleyelim
    for player_id, player_name, assists, player_country in assist_list:
        if player_id not in contributions:
            contributions[player_id] = {
                "player_name": player_name,
                "player_country": player_country,
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
            details["player_country"],
        )
        for player_id, details in contributions.items()
    ]

    # Toplam katkıya göre azalan sırada sırala
    combined_list.sort(key=lambda x: x[2], reverse=True)

    # İlk 5 oyuncuyu döndür
    return combined_list[:5]


@club_bp.route('/')
def get_clubs():
    try:

        name = request.args.get('name', '').strip()
        official_name = request.args.get('official_name', '').strip()
        country = request.args.get('country')
        stadium = request.args.get('stadium')
        query = """
        SELECT c.id, c.name, c.officialname, c.country, s.stadium
        FROM club c
        LEFT JOIN stadiums s ON c.stadiums_id = s.id
        WHERE 1=1
        """
        params = []

        if name:
            query += " AND c.name ILIKE %s"
            params.append(f"%{name}%")
        if official_name:
            query += " AND c.officialname ILIKE %s"
            params.append(f"%{official_name}%")
        if country:
            query += " AND c.country = %s"
            params.append(country)
        if stadium:
            query += " AND c.stadiums_id = %s"
            params.append(stadium)

        query += " ORDER BY c.name;"

        clubs = db.executeQuery(query, params)
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

        countries = [{"id": row[0], "name": row[1]} for row in db.executeQuery("SELECT id, country FROM countries ORDER BY country;")]
        stadiums = db.executeQuery("SELECT id, stadium FROM stadiums ORDER BY stadium;")

    except Exception as e:
        clubs = []
        countries = []
        stadiums = []
        print(f"Error fetching clubs: {e}")

    return render_template('club/index.html', clubs=clubs, countries=countries, stadiums=stadiums, filters=request.args)

@club_bp.route('/<int:id>')
def get_club(id):
    """Fetches and displays details of a single club by ID."""
    try:
        query = """
        SELECT c.id, c.name, c.officialname, c.country, s.stadium, co.id, fm.competition, s.city, s.id
        FROM club c
        LEFT JOIN stadiums s ON c.stadiums_id = s.id
        LEFT JOIN countries co ON c.country = co.country
        LEFT JOIN football_match fm ON c.id = home_club
        WHERE c.id = %s;
        """
        club_data = db.executeQuery(query, params=(id,))
        if not club_data:
            flash(f"Club with ID {id} not found.", 'danger')
            return redirect(url_for('club.get_clubs'))

        club = {
            "id": club_data[0][0],
            "name": club_data[0][1],
            "officialname": club_data[0][2],
            "country": club_data[0][3],
            "stadium": club_data[0][4],
            "country_id": club_data[0][5],
            "league": club_data[0][6],
            "city": club_data[0][7],
            "sid": club_data[0][8]
        }

        # Fetch additional statistics and players data
        match_count = db.executeQuery("""
            SELECT COUNT(*) FROM football_match 
            WHERE home_club = %s OR away_club = %s;
        """, params=(id, id))[0][0] or 0

        win_count = db.executeQuery("""
            SELECT COUNT(*) 
            FROM football_match 
            WHERE (home_club = %s AND winner = %s) OR (away_club = %s AND winner = %s);
        """, params=(id, id, id, id))[0][0] or 0

        loss_count = db.executeQuery("""
            SELECT COUNT(*) 
            FROM football_match 
            WHERE (home_club = %s AND winner != %s) OR (away_club = %s AND winner != %s);
        """, params=(id, id, id, id))[0][0] or 0

        goal_scored = db.executeQuery("""
            SELECT 
                SUM(CASE WHEN home_club = %s THEN goal_by_home_club ELSE 0 END) + 
                SUM(CASE WHEN away_club = %s THEN goal_by_away_club ELSE 0 END)
            FROM football_match 
            WHERE home_club = %s OR away_club = %s;
        """, params=(id, id, id, id))[0][0] or 0

 
        goal_conceded = db.executeQuery("""
            SELECT 
                SUM(CASE WHEN home_club = %s THEN goal_by_away_club ELSE 0 END) + 
                SUM(CASE WHEN away_club = %s THEN goal_by_home_club ELSE 0 END)
            FROM football_match 
            WHERE home_club = %s OR away_club = %s;
        """, params=(id, id, id, id))[0][0] or 0

        
        cln_sheet = db.executeQuery("""
            SELECT COUNT(*) 
            FROM football_match 
            WHERE (home_club = %s AND goal_by_away_club = 0) OR (away_club = %s AND goal_by_home_club = 0);
        """, params=(id, id))[0][0] or 0

        # Top scorers, assists, and goal contributions
        top_scorers = get_top_scorers(id)
        scorer_player_images = load_player_images(top_scorers)

        top_assists = get_top_assists(id)
        assist_player_images = load_player_images(top_assists)

        top_contributions = get_top_contributions(top_scorers, top_assists)
        cont_player_images = load_player_images(top_contributions)

        match_history = db.executeQuery(MATCHES_QUERY, params=(id, id))


    except Exception as e:
        print(f"Error fetching club details: {e}")
        print("Traceback:")
        print(traceback.format_exc())
        flash("Error fetching club details.", "danger")
        return redirect(url_for('club.get_clubs'))

    return render_template('club/details.html', 
                           club=club, 
                           match_count=match_count, 
                           win_count=win_count,
                           loss_count=loss_count,
                           goal_scored=goal_scored, 
                           goal_conceded=goal_conceded,
                           cln_sheet = cln_sheet,
                           top_scorers=top_scorers,
                           top_assists=top_assists, 
                           top_contributions=top_contributions,
                           match_history=match_history,
                           scorer_player_images=scorer_player_images,
                           assist_player_images=assist_player_images,
                           cont_player_images=cont_player_images
                           )


@club_bp.route('/add', methods=['GET', 'POST'])
@isAdmin
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
@isAdmin
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
@isAdmin
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
