from flask import Blueprint, render_template, flash, redirect, url_for
from collections import defaultdict
from database import db

match_details_bp = Blueprint('match_details', __name__, template_folder="templates")

def convert_to_dict(events, column_names):
    return [dict(zip(column_names, event)) for event in events]

def convert_coordinates(shot_data, is_home_team):
    converted_shots = []
    field_length = 105
    field_width = 68

    for shot in shot_data:
        if is_home_team:
            # Home team left-to-right attack
            x = shot['x_begin'] * field_length / 100
            y = shot['y_begin'] * field_width / 100
        else:
            # Away team right-to-left attack
            x = field_length - (shot['x_begin'] * field_length / 100)
            y = shot['y_begin'] * field_width / 100

        converted_shots.append({'x': x, 'y': y})

    return converted_shots

def extract_shot_coordinates(events):
        home_shots = []
        away_shots = []
        for event in events:
            if event['eventname'] == 'Shot': 
                shot_data = {
                    'x_begin': event['x_begin'],
                    'y_begin': event['y_begin'],
                    'x_end': event['x_end'],
                    'y_end': event['y_end']
                }
                if event['is_home_team']:
                    home_shots.append(shot_data)
                else:
                    away_shots.append(shot_data)
        return home_shots, away_shots    

@match_details_bp.route('/match/<int:id>')
def match_details(id):
    """Fetch and display match details and events."""

    match_query = """
    SELECT 
        c.country AS Country,
        c.region AS Region,
        s.city AS City,
        s.stadium AS Stadium,
        s.capacity AS Capacity,
        hc.name AS "Home Team",
        ac.name AS "Away Team",
        wc.name AS Winner,
        fm.dateutc AS Date,
        fm.competition AS Competition,
        fm.goal_by_home_club AS "Home Team Score",
        fm.goal_by_away_club AS "Away Team Score"
    FROM football_match_event e
    JOIN football_match fm ON e.football_match_id = fm.id
    JOIN club hc ON fm.home_club = hc.id
    JOIN club ac ON fm.away_club = ac.id
    LEFT JOIN club wc ON fm.winner = wc.id
    JOIN stadiums s ON fm.stadiums_id = s.id
    JOIN countries c ON s.country_id = c.id
    WHERE e.football_match_id = %s;
    """
    match_info = db.executeQuery(match_query, params=(id,))

    if not match_info or not match_info[0]:
        flash(f"Match with ID {id} not found.", "danger")
        return redirect(url_for('home'))

    event_query = """
    SELECT 
        e.id AS event_id, 
        cl.name AS team_name, 
        CONCAT(p.firstname, ' ', p.lastname) AS player_name, 
        e.matchperiod, 
        e.eventsec, 
        e.eventname, 
        e.action, 
        e.modifier, 
        e.x_begin, 
        e.y_begin, 
        e.x_end, 
        e.y_end, 
        e.is_success,
        CASE 
            WHEN e.club_id = fm.home_club THEN TRUE 
            ELSE FALSE 
        END AS is_home_team
    FROM 
        football_match_event e
    LEFT JOIN 
        club cl ON e.club_id = cl.id
    LEFT JOIN 
        player p ON e.player_id = p.id
    LEFT JOIN 
        football_match fm ON e.football_match_id = fm.id
    WHERE 
        e.football_match_id = %s
    ORDER BY 
        e.eventname, e.eventsec;
    """
    events = db.executeQuery(event_query, params=(id,))

    if not events:
        flash("No events found for this match.", "info")

    column_names = ['event_id', 'team_name', 'player_name', 'matchperiod', 'eventsec',
                    'eventname', 'action', 'modifier', 'x_begin', 'y_begin', 'x_end', 'y_end',
                    'is_success', 'is_home_team']
    
    events_dict = convert_to_dict(events, column_names)

    home_events = [event for event in events_dict if event['is_home_team']]
    away_events = [event for event in events_dict if not event['is_home_team']]

    def calculate_event_widths(home_events, away_events):
        home_event_counts = defaultdict(int)
        away_event_counts = defaultdict(int)
        widths = []

        for event in home_events:
            home_event_counts[event['eventname']] += 1
        for event in away_events:
            away_event_counts[event['eventname']] += 1

        all_event_names = set(home_event_counts.keys()).union(set(away_event_counts.keys()))
        for eventname in all_event_names:
            home_count = home_event_counts.get(eventname, 0)
            away_count = away_event_counts.get(eventname, 0)
            total = home_count + away_count
            if total > 0:
                home_width = (home_count / total) * 100
                away_width = (away_count / total) * 100
            else:
                home_width = 50
                away_width = 50
            widths.append({
                'eventname': eventname,
                'home_count': home_count,
                'away_count': away_count,
                'home_width': home_width,
                'away_width': away_width,
            })

        return widths

    event_widths = calculate_event_widths(home_events, away_events)

    home_shots_raw, away_shots_raw = extract_shot_coordinates(events_dict)
    home_shots = convert_coordinates(home_shots_raw, is_home_team=True)
    away_shots = convert_coordinates(away_shots_raw, is_home_team=False)

    return render_template(
        'stats/match_stats.html',
        match=match_info[0],
        home_shots=home_shots,
        away_shots=away_shots,
        event_widths=event_widths
    )
