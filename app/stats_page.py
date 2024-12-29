from flask import Blueprint, render_template, flash, redirect, url_for
from collections import defaultdict
from math import ceil, sqrt
import csv
from database import db
import json
from match import get_matches

GET_MATCH_INFO_QUERY = """
    SELECT DISTINCT
        c.country AS Country,
        s.city AS City,
        s.stadium AS Stadium,
        s.capacity AS Capacity,
		fm.home_club AS "Home ID",
        fm.away_club AS "Away ID",
        hc.name AS "Home Team",
        ac.name AS "Away Team",
        fm.dateutc AS Date,
        fm.competition AS Competition,
        fm.goal_by_home_club AS "Home Team Score",
        fm.goal_by_away_club AS "Away Team Score"

FROM football_match_event e
JOIN football_match fm ON e.football_match_id = fm.id
JOIN club hc ON fm.home_club = hc.id
JOIN club ac ON fm.away_club = ac.id
JOIN stadiums s ON fm.stadiums_id = s.id
JOIN countries c ON s.country_id = c.id
WHERE e.football_match_id = %s;
"""

GET_EVENTS_QUERY = """
SELECT 
    e.eventname,
    e.action,
    e.modifier,
    e.is_success,
    CASE WHEN e.club_id = fm.home_club THEN TRUE ELSE FALSE END AS is_home_team
FROM football_match_event e
LEFT JOIN football_match fm ON e.football_match_id = fm.id
WHERE 1=1

"""

GET_GOALS_QUERY = """
WITH params AS (
    SELECT 
        %s AS match_id,
        %s AS team_type 
),
filtered_events AS (
    SELECT 
		e.id, e.club_id, e.player_id,
        e.matchperiod, e.eventsec, e.action,
        CASE 
            WHEN params.team_type = 0 THEN fm.home_club
            WHEN params.team_type = 1 THEN fm.away_club
        END AS team_id
    FROM football_match_event e
    LEFT JOIN football_match fm ON e.football_match_id = fm.id
    CROSS JOIN params
    WHERE 
        e.football_match_id = params.match_id
        AND e.eventname = 'Save attempt'
        AND e.is_success = FALSE
        AND e.club_id = CASE 
            WHEN params.team_type = 0 THEN fm.away_club
            WHEN params.team_type = 1 THEN fm.home_club
        END
)
SELECT 
    e.id,
    e.player_id,
    p.firstname || ' ' || p.lastname AS name,
    e.matchperiod, e.eventsec,
    CASE 
        WHEN fe.team_id = e.club_id THEN FALSE
        ELSE TRUE
    END AS is_og,
    CASE 
        WHEN e.action = 'Penalty' THEN TRUE
        ELSE FALSE
    END AS is_penalty
FROM football_match_event e
JOIN filtered_events fe ON e.id = fe.id - 1
JOIN player p ON e.player_id = p.id
CROSS JOIN params
WHERE e.football_match_id = params.match_id
"""

GET_STARTING_XI_QUERY = """
SELECT 
    p.id AS player_id,
    CONCAT(p.firstname, ' ', p.lastname) AS player_name,
    CASE 
        WHEN p.position = 'Goalkeeper' THEN 'GK'
        WHEN p.position = 'Defender' THEN 'DF'
        WHEN p.position = 'Midfielder' THEN 'MF'
        WHEN p.position = 'Forward' THEN 'FW'
        ELSE p.position
    END AS position,
    p.country_id
FROM 
    (
        SELECT DISTINCT ON (fe.player_id) 
            fe.player_id, 
            fe.eventsec,
            fe.club_id
        FROM 
            football_match_event fe,
            (SELECT 
                %s AS match_id, 
                %s AS club_type
            ) params,
            football_match fm
        WHERE 
            fe.football_match_id = params.match_id
            AND fe.matchperiod = '1H'
            AND fe.club_id = CASE 
                WHEN params.club_type = 0 THEN fm.home_club
                WHEN params.club_type = 1 THEN fm.away_club
            END
            AND fm.id = params.match_id
        ORDER BY 
            fe.player_id, fe.eventsec ASC
    ) AS first_events
JOIN 
    player p ON first_events.player_id = p.id
ORDER BY 
    first_events.eventsec ASC
LIMIT 11;

"""

GET_LAST_5_MATCHES_QUERY = """
WITH
    params AS (
        SELECT 
            %s AS match_id,  
            %s AS club_type   
    ),
    target_club AS (
        SELECT 
            CASE 
                WHEN params.club_type = 0 THEN fm.home_club
                WHEN params.club_type = 1 THEN fm.away_club
            END AS club_id,
            fm.dateutc AS match_date
        FROM football_match fm, params
        WHERE fm.id = params.match_id
    )
SELECT 
    fm.id AS match_id, 
    fm.dateutc AS match_date,
    CASE 
        WHEN fm.home_club = target_club.club_id AND fm.winner = fm.home_club THEN 'WIN'
        WHEN fm.away_club = target_club.club_id AND fm.winner = fm.away_club THEN 'WIN'
        ELSE 'LOSS'
    END AS result,
    fm.home_club, 
    fm.away_club, 
    fm.goal_by_home_club, 
    fm.goal_by_away_club
FROM football_match fm, target_club
WHERE 
    fm.dateutc < target_club.match_date
    AND (fm.home_club = target_club.club_id OR fm.away_club = target_club.club_id)
ORDER BY 
    fm.dateutc DESC 
LIMIT 5;
"""


GET_SUBSTITUTIONS_QUERY  = """
WITH
    params AS (
        SELECT 
            %s AS match_id,  
            %s AS club_type   
    ),
    club_selection AS (
        SELECT 
            CASE 
                WHEN params.club_type = 0 THEN fm.home_club
                WHEN params.club_type = 1 THEN fm.away_club
            END AS selected_club
        FROM football_match fm, params
        WHERE fm.id = params.match_id
    )
SELECT 
    p.id AS player_id,
    p.firstname,
    p.lastname,
    (SELECT fme.matchperiod 
     FROM football_match_event fme, params, club_selection
     WHERE fme.player_id = p.id 
       AND fme.football_match_id = params.match_id
       AND fme.club_id = club_selection.selected_club
     ORDER BY fme.matchperiod ASC, fme.eventsec ASC
     LIMIT 1) AS firstPeriod,
    (SELECT fme.eventsec 
     FROM football_match_event fme, params, club_selection
     WHERE fme.player_id = p.id 
       AND fme.football_match_id = params.match_id
       AND fme.club_id = club_selection.selected_club
     ORDER BY fme.matchperiod ASC, fme.eventsec ASC
     LIMIT 1) AS firstSec,


    (SELECT fme.matchperiod 
     FROM football_match_event fme, params, club_selection
     WHERE fme.player_id = p.id 
       AND fme.football_match_id = params.match_id
       AND fme.club_id = club_selection.selected_club
     ORDER BY fme.matchperiod DESC, fme.eventsec DESC
     LIMIT 1) AS lastPeriod,
    (SELECT fme.eventsec 
     FROM football_match_event fme, params, club_selection
     WHERE fme.player_id = p.id 
       AND fme.football_match_id = params.match_id
       AND fme.club_id = club_selection.selected_club
     ORDER BY fme.matchperiod DESC, fme.eventsec DESC
     LIMIT 1) AS lastSec,
    (SELECT fme.modifier 
     FROM football_match_event fme, params, club_selection
     WHERE fme.player_id = p.id 
       AND fme.football_match_id = params.match_id
       AND fme.club_id = club_selection.selected_club
     ORDER BY fme.matchperiod DESC, fme.eventsec DESC
     LIMIT 1) AS lastModifier
FROM 
    player p
WHERE 
    EXISTS (
        SELECT 1 
        FROM football_match_event fme, params, club_selection
        WHERE fme.player_id = p.id 
          AND fme.football_match_id = params.match_id
          AND fme.club_id = club_selection.selected_club
          AND fme.action != 'Out of game foul'
    );
"""

GET_CARDS_QUERY= """
WITH params AS (
    SELECT 
        %s AS match_id,
        %s AS club_type
),
club_selection AS (
    SELECT 
        CASE 
            WHEN params.club_type = 0 THEN fm.home_club
            WHEN params.club_type = 1 THEN fm.away_club
        END AS selected_club
    FROM football_match fm, params
    WHERE fm.id = params.match_id
)
SELECT 
    fme.player_id,
    p.firstname,
    p.lastname,
    fme.matchperiod AS period,
    fme.eventsec,
    fme.action,
    fme.modifier
FROM 
    football_match_event fme
JOIN 
    player p ON fme.player_id = p.id
JOIN 
    club_selection cs ON fme.club_id = cs.selected_club
JOIN 
    params ON fme.football_match_id = params.match_id
WHERE 
    fme.modifier IN ('red_card', 'second_yellow_card', 'yellow_card')
"""

GET_EVENTS_BASE_QUERY = '''
SELECT 
  e.id, 
  e.club_id, 
  e.player_id,
  p.firstname,
  p.lastname,
  e.matchperiod, 
  e.eventsec, 
  e.action, 
  e.modifier, 
  e.x_begin, 
  e.y_begin, 
  e.x_end, 
  e.y_end, 
  e.is_success,
CASE WHEN e.club_id = fm.home_club THEN TRUE ELSE FALSE END AS is_home_team
FROM football_match_event e
LEFT JOIN football_match fm ON e.football_match_id = fm.id
LEFT JOIN player p ON p.id = e.player_id
WHERE 
  e.football_match_id = %s 
'''

GET_SHOTS_QUERY = """
  AND (eventname = 'Shot' 
  OR action = 'Free kick shot' 
  OR action = 'Penalty')
"""

GET_PASSES_QUERY = """
  AND eventname = 'Pass'
"""

GET_INTERCEPTIONS_QUERY = '''
  AND action= 'Touch' AND modifier = 'interception'
'''

GET_OFFSIDES_QUERY = '''
  AND eventname = 'Offside'
'''

GET_DUELS_QUERY= '''
    AND eventname = 'Duel' AND modifier= 'won'
'''

GET_FOULS_QUERY= '''
    AND eventname = 'Foul'
'''

GET_FREEKICKS_QUERY= '''
    AND eventname = 'Free Kick' AND (action = 'Free Kick' OR action = 'Free kick shot' OR action = 'Free kick cross')
'''

GET_SAVES_QUERY= '''
    AND eventname='Save attempt' and is_success= true and (x_end !=0 and y_end != 0)
'''



match_details_bp = Blueprint('match_details', __name__, template_folder="templates")


def load_player_images(starters, subs):
    all_ids = {p["id"] for p in starters} | {p["sub_on_id"] for p in subs if "sub_on_id" in p}
    player_data = {}
    with open('app/static/images/player_images.csv', mode='r') as file:
        for row in csv.DictReader(file):
            dset_id = int(row['dataset_ID'])
            if dset_id in all_ids:
                player_data[dset_id] = row['link']
    return player_data

def calculate_distance(x1, y1, x2, y2):
    return round(sqrt((x2 - x1)**2 + (y2 - y1)**2), 2)

def normalize_name(name):
    if len(name) > 18:
        parts = name.split()
        if len(parts) > 1:
            return f"{parts[0][0]}. {parts[-1]}"

    return name    

def normalize_minute(minute):
    if isinstance(minute, str) and '+' in minute:
        base, extra = minute.split('+')
        return int(base) + int(extra)
    return int(minute)

def get_match_info(match_id):
    result = db.executeQuery(GET_MATCH_INFO_QUERY, params=(match_id,))
    match_info = {}
    if result:
        row = result[0]
        match_info = {
            "country": row[0],
            "city": row[1],
            "stadium": row[2],
            "capacity": row[3],
            "home_id": row[4],
            "away_id": row[5],
            "home_name": row[6],
            "away_name": row[7],
            "date": row[8],
            "league": row[9],
            "home_score": row[10],
            "away_score": row[11]
        }

    return match_info

def get_cards(match_id, is_home):
    result = db.executeQuery(GET_CARDS_QUERY, params=(match_id, is_home))
    cards = []
    for card in result:
        player_id, firstname, lastname, period, eventsec, action, modifier = card
        minute = calculate_minute(period, eventsec)
        cards.append({
            "player_id": player_id,
            "firstname": firstname,
            "lastname": lastname,
            "period": period,
            "minute": minute,
            "action": action,
            "modifier": modifier
        })
    return cards

def get_key_events(home_goals, home_subs, home_cards, away_goals, away_subs, away_cards):

    key_events = []
    home_score = 0
    away_score = 0
    all_goals = (home_goals + away_goals)
    all_goals.sort(key=lambda x: (x["period"], normalize_minute(x["minute"])))

    for goal in all_goals :
        if (goal in home_goals):
            home_score+= 1
        else:
            away_score += 1
        details_up = normalize_name(goal["player_name"])
        details_down = f"{home_score}-{ away_score} "
        icon = "goal"
        if goal["is_own_goal"]:
            icon += "_og"
            details_down += "Own Goal"
        elif goal["is_penalty"]:
            icon += "_p"
            details_down += "Penalty"
        is_home = (goal in home_goals) & (goal["is_own_goal"] != True)
        key_events.append({
            "player_id": goal["player_id"],
            "icon": icon,
            "details_up": details_up,
            "details_down": details_down,
            "period": goal["period"],
            "minute": goal["minute"],
            "is_home": is_home
        })

    for sub in (home_subs + away_subs):
        is_home = sub in home_subs
        key_events.append({
            "player_id": sub["sub_on_id"],
            "icon": "sub",
            "details_up": normalize_name(sub["sub_on_name"]),
            "details_down": normalize_name(sub["sub_off_name"]),
            "period": sub["period"],
            "minute": sub["minute"],
            "is_home": is_home
        })

    for card in (home_cards + away_cards):
        name_concat = f"{card['firstname']} {card['lastname']}"
        details_up = normalize_name(name_concat)
        is_home = card in home_cards
        key_events.append({
            "player_id": card["player_id"],
            "icon": card["modifier"],
            "details_up": details_up,
            "details_down": card["action"],
            "period": card["period"],
            "minute": card["minute"],
            "is_home": is_home
        })

    key_events.sort(key=lambda x: (x["period"], normalize_minute(x["minute"])))

    return key_events

def calculate_minute(period, sec):
    minute = ceil(sec / 60) + (45 if period == '2H' else 0)
    if minute > 45 and period == '1H':
        return f"45+{minute - 45}"
    elif minute > 90 and period == '2H':
        return f"90+{minute - 90}"
    return minute


def get_goals(match_id, is_home):
    result = db.executeQuery(GET_GOALS_QUERY, params=(match_id, is_home))

    goals = []
    for row in result:
        event_id, player_id, player_name, period, seconds, is_own_goal, is_penalty = row

        minute = calculate_minute(period, seconds)
        player_name = normalize_name(player_name)

        goals.append({
            "event_id": event_id,
            "player_id": player_id,
            "player_name": player_name,
            "period": period,
            "minute": minute,
            "is_own_goal": is_own_goal,
            "is_penalty": is_penalty
        })
    return goals


def merge_players(xi, subs):
    merged_players = []
    
    for player in xi:
        merged_players.append({'id': player['id'], 'name': normalize_name(player['name']) })
    
    for player in subs:
        merged_players.append({'id': player['sub_on_id'], 'name': normalize_name(player['sub_on_name'])})
    
    return merged_players

def get_shot_end_coordinate(modifier, is_home):
    end_x_coordinate =(
        0 if is_home else
        105
    )

    end_y_coordinate = (
        39.5 if (modifier in ["otl", "ol", "olb"]) & is_home else
        28.5 if (modifier in ["otr", "or", "obr"]) & is_home else
        35.83 if (modifier in ["gtl", "gl", "glb"]) & is_home else
        34 if (modifier in ["ot", "gt", "gc", "gb", "pt"]) & is_home else
        32.17 if (modifier in ["gtr", "gr", "gbr"]) & is_home else
        30.34 if (modifier in ["pbr", "pr", "ptr"]) & is_home else
        37.66 if (modifier in ["plb", "pl", "ptl"]) & is_home else
            
        (68-39.5) if modifier in ["otl", "ol", "olb"] else
        (68-29.5) if modifier in ["otr", "or", "obr"] else
        (68-35.83) if modifier in ["gtl", "gl", "glb"] else
        (68-34) if modifier in ["ot", "gt", "gc", "gb", "pt"] else
        (68-32.17) if modifier in ["gtr", "gr", "gbr"] else
        (68-30.34) if modifier in ["pbr", "pr", "ptr"] else
        (68-37.66) if modifier in ["plb", "pl", "ptl"] else
        -1
    )

    return end_x_coordinate, end_y_coordinate

def convert_coordinates(x_begin, y_begin, is_home):
    field_length, field_width = 105, 68
    new_x = 0
    new_y = 0
    if is_home:
        new_x = round((field_length - (x_begin * field_length / 100)),2)
        new_y = round((y_begin * field_width / 100),2)
    else:
        new_x = round((x_begin * field_length / 100),2)
        new_y = round((field_width - (y_begin * field_width / 100)),2)
    return new_x, new_y

def get_shots(match_id, goals):
    query_result = db.executeQuery(GET_EVENTS_BASE_QUERY + GET_SHOTS_QUERY , params=(match_id,))
    shots = []

    for row in query_result:
        event_id, club_id, player_id, first_name, last_name, matchperiod, eventsec, action, modifier, x_begin, y_begin, x_end, y_end, is_success, is_home = row

        minute = calculate_minute(matchperiod, eventsec)
        player_name = normalize_name(first_name + " " + last_name)
        x_coordinate, y_coordinate = convert_coordinates(x_begin, y_begin,is_home)
        result = ""
        is_goal = any(goal["event_id"] == event_id for goal in goals)


        distance = (
            calculate_distance(x_coordinate, y_coordinate, 0, 34) if is_home else
            calculate_distance(x_coordinate, y_coordinate, 105, 34) 
        )

        end_x_coordinate, end_y_coordinate = get_shot_end_coordinate(modifier, is_home)
        
        result = (
            "Goal" if is_goal else
            "Save" if modifier in ["gb", "gbr", "gc", "gl", "glb", "gr", "gt", "gtl", "gtr"] else
            "Blocked" if modifier == "blocked" else
            "Intercepted" if modifier == "interception" else
            "Opportunity Missed" if modifier == "opportunity" else
            "Miss" if modifier in ["obr", "ol", "olb", "or", "ot", "otl", "otr"] else
            "Post" if modifier in ["pbr", "pl", "plb", "pr", "pt", "ptl", "ptr"] else
            ""
        )

        situation = (
            "Regular play" if action == "Shot" else
            "Penalty" if action == "Penalty" else
            "Free Kick" if action == "Free kick shot" else
            ""
        )

        shots.append({
            "event_id": event_id,
            "player_id": player_id,
            "player_name": player_name,
            "club_id": club_id,
            "is_home": is_home,
            "period": matchperiod,
            "minute": minute,
            "action": action,
            "modifier": modifier,
            "x_coordinate": x_coordinate,
            "y_coordinate": y_coordinate,
            "is_success": is_success,
            "end_x_coordinate": end_x_coordinate,
            "end_y_coordinate": end_y_coordinate,
            "distance": distance,
            "result": result,
            "situation": situation
                            })
    return shots

def get_events(match_id, event_query, type):
    query_result = db.executeQuery(GET_EVENTS_BASE_QUERY + event_query, params=(match_id,))
    passes = []

    for row in query_result:
        event_id, club_id, player_id, first_name, last_name, matchperiod, eventsec, action, modifier, x_begin, y_begin, x_end, y_end, is_success, is_home = row
        minute = calculate_minute(matchperiod, eventsec)
        player_name = normalize_name(first_name + " " + last_name)
        
        
        if not any(c is None for c in [x_begin, y_begin, x_end, y_end]):
            if(type in ['offside' , 'foul']):
                x_coordinate, y_coordinate = convert_coordinates(x_begin, y_begin,is_home)
                end_x_coordinate, end_y_coordinate = -1, -1
                distance = ""
            elif(type == 'save'):
                x_coordinate, y_coordinate = convert_coordinates(x_end, y_end,is_home)
                end_x_coordinate, end_y_coordinate = -1, -1
                distance = ""
            elif(type == 'freekick' and action == 'Free kick shot'):
                x_coordinate, y_coordinate = convert_coordinates(x_begin, y_begin,is_home)
                end_x_coordinate, end_y_coordinate = get_shot_end_coordinate(modifier, is_home)
                distance = (
                calculate_distance(x_coordinate, y_coordinate, end_x_coordinate, end_y_coordinate))
            else:
                x_coordinate, y_coordinate = convert_coordinates(x_begin, y_begin,is_home)
                end_x_coordinate, end_y_coordinate = convert_coordinates(x_end, y_end,is_home)
                distance = (
                calculate_distance(x_coordinate, y_coordinate, end_x_coordinate, end_y_coordinate)
        )
        else:
            x_coordinate = -1
            y_coordinate = -1
            end_x_coordinate = -1
            end_y_coordinate = -1
            distance = ""



        passes.append({
            "event_id": event_id,
            "player_id": player_id,
            "player_name": player_name,
            "club_id": club_id,
            "is_home": is_home,
            "period": matchperiod,
            "minute": minute,
            "action": action,
            "modifier": modifier,
            "x_coordinate": x_coordinate,
            "y_coordinate": y_coordinate,
            "is_success": is_success,
            "end_x_coordinate": end_x_coordinate,
            "end_y_coordinate": end_y_coordinate,
            "distance": distance,
            "result": "",
            "situation": ""
        })
    return passes


def calculate_metric_widths(match_id):
    metrics = {
    'Total Shots': {'eventname': None, 'action': ['Shot', 'Free kick shot', 'Penalty'], 'modifier': None, 'is_success': None},
    'Accurate Shots': {'eventname': 'Shot', 'action': None, 'modifier': None, 'is_success': True},
    'Goalkeeper Saves': {'eventname': 'Save attempt', 'action': None, 'modifier': None, 'is_success': True},
    'Corners': {'eventname': None, 'action': 'Corner', 'modifier': None, 'is_success': None},
    'Offsides': {'eventname': 'Offside', 'action': None, 'modifier': None, 'is_success': None},
    'Fouls': {'eventname': 'Foul', 'action': None, 'modifier': None, 'is_success': None},
    'Passes': {'eventname': 'Pass', 'action': None, 'modifier': None, 'is_success': None},
    'Accurate Passes': {'eventname': 'Pass', 'action': None, 'modifier': None, 'is_success': True},
    'Free Kicks': {'eventname': 'Free Kick', 'action': ['Free Kick', 'Free kick shot', 'Free kick cross'], 'modifier': None, 'is_success': None},
    'Throw-ins': {'eventname': 'Free Kick', 'action': 'Throw in', 'modifier': None, 'is_success': None},
    'Yellow Cards': {'eventname': 'Foul', 'action': None, 'modifier': 'yellow_card', 'is_success': None},
    'Red Cards': {'eventname': 'Foul', 'action': None, 'modifier': ['red_card', 'second_yellow_card'], 'is_success': None},
    'Shots on Target': {'eventname': None, 'action': ['Shot', 'Free kick shot', 'Penalty'], 'modifier': None, 'is_success': True},
    'Shots Hit Post': {'eventname': None, 'action': ['Shot', 'Free kick shot', 'Penalty'], 'modifier': ['pbr', 'pl', 'plb', 'pr', 'pt', 'ptl', 'ptr'], 'is_success': None},
    'Missed Shots': {'eventname': None, 'action': ['Shot', 'Free kick shot', 'Penalty'], 'modifier': ['obr', 'ol', 'olb', 'opportunity', 'or', 'ot', 'otl', 'otr'], 'is_success': None},
    'Blocked Shots': {'eventname': None, 'action': ['Shot', 'Free kick shot', 'Penalty'], 'modifier': ['blocked', 'interception'], 'is_success': None},
    'Accurate Long Passes': {'eventname': 'Pass', 'action': 'High pass', 'modifier': None, 'is_success': True},
    'Accurate Crosses': {'eventname': 'Pass', 'action': 'Cross', 'modifier': None, 'is_success': True},
    'Key Passes': {'eventname': 'Pass', 'action': 'Smart pass', 'modifier': None, 'is_success': None},
    'Interceptions': {'eventname': None, 'action': None, 'modifier': 'interception', 'is_success': None},
    'Clearances': {'eventname': None, 'action': 'Clearance', 'modifier': ['counter_attack', 'dangerous_ball_lost', 'fairplay', 'interception', 'missed ball', 'own_goal'], 'is_success': None},
    'Duel Wins': {'eventname': 'Duel', 'action': None, 'modifier': 'won', 'is_success': None}
}

    widths = []

    for metric_name, metric_data in metrics.items():
        conditions = []
        query_params = []

        conditions.append("AND e.football_match_id = %s")
        query_params.append(match_id)

        if metric_data['eventname'] is not None:
            conditions.append("AND e.eventname = %s")
            query_params.append(metric_data['eventname'])

        if metric_data['action'] is not None:
            if isinstance(metric_data['action'], list):
                conditions.append("AND e.action = ANY(%s)")
                query_params.append(metric_data['action'])
            else:
                conditions.append("AND e.action = %s")
                query_params.append(metric_data['action'])

        if metric_data['modifier'] is not None:
            if isinstance(metric_data['modifier'], list):
                conditions.append("AND e.modifier = ANY(%s)")
                query_params.append(metric_data['modifier'])
            else:
                conditions.append("AND e.modifier = %s")
                query_params.append(metric_data['modifier'])

        if metric_data['is_success'] is not None:
            conditions.append("AND e.is_success = %s")
            query_params.append(metric_data['is_success'])

        final_query = " ".join([GET_EVENTS_QUERY] + conditions)

        result = db.executeQuery(final_query, query_params)

        h_count = sum(1 for row in result if row[4])
        a_count = sum(1 for row in result if not row[4])
        total = h_count + a_count

        if total > 0:
            h_w, a_w = (h_count / total) * 100, (a_count / total) * 100
        else:
            h_w, a_w = 0, 0

        widths.append({
                'metric': metric_name,
                'home_count': h_count,
                'away_count': a_count,
                'home_width': h_w,
                'away_width': a_w
        })

    best_weights = {
        'Passes': 0.1, 'Accurate Passes': 0.1, 'Accurate Long Passes': 0.2,
        'Throw-ins': 0.45, 'Interceptions': 0.45, 'Clearances': 0.1
    }

    home_score = sum(
        best_weights[m] * next((w['home_count'] for w in widths if w['metric'] == m), 0)
        for m in best_weights
    )
    away_score = sum(
        best_weights[m] * next((w['away_count'] for w in widths if w['metric'] == m), 0)
        for m in best_weights
    )

    total_score = home_score + away_score
    if total_score > 0:
        home_pos = round((home_score / total_score) * 100, 1)
        away_pos = round((away_score / total_score) * 100, 1)
    else:
        home_pos, away_pos = 50.0, 50.0

    widths.insert(0, {
        'metric': "Possession",
        'home_count': home_pos,
        'away_count': away_pos,
        'home_width': home_pos,
        'away_width': away_pos
    })

    return widths

def get_substitutions(match_id, is_home):
    substitutions = db.executeQuery(GET_SUBSTITUTIONS_QUERY, params=(match_id, is_home))
    sub_count = len(substitutions) - 11
    filtered_subs = [sub for sub in substitutions if sub[7] not in ('red_card', 'second_yellow_card')]

    sorted_sub_on = sorted(filtered_subs, key=lambda x: (x[3], x[4]), reverse=True)
    sub_on_group = sorted_sub_on[:sub_count]

    sorted_sub_off = sorted(filtered_subs, key=lambda x: (x[5], x[6]))
    sub_off_group = sorted_sub_off[:sub_count]

    sub_on_group = sorted(sub_on_group, key=lambda x: (x[3], x[4]))
    sub_off_group = sorted(sub_off_group, key=lambda x: (x[5], x[6]))
    result = []
    for sub_on, sub_off in zip(sub_on_group, sub_off_group):
        if sub_on != sub_off:
            minute = calculate_minute(sub_off[5], sub_off[6])
            period = sub_off[5]

            result.append({
                "sub_on_id": sub_on[0],
                "sub_on_name": f"{sub_on[1]} {sub_on[2]}",
                "period": period,
                "minute": minute,
                "sub_off_id": sub_off[0],
                "sub_off_name": f"{sub_off[1]} {sub_off[2]}"

            })

    return result

def get_starting_XI(match_id, is_home):
    result = db.executeQuery(GET_STARTING_XI_QUERY, params=(match_id, is_home))

    starting_XI = []
    for p_id, p_name, pos, c_id in result:
        if len(p_name) > 15:
            parts = p_name.split()
            if len(parts) > 1:
                p_name = f"{parts[0][0]}. {parts[-1]}"

        starting_XI.append({
            "id": p_id,
            "name": p_name,
            "position": pos,
            "country_id": c_id
        })

    position_priority = {"GK": 1, "DF": 2, "MF": 3, "FW": 4}

    sorted_XI = sorted(
        starting_XI,
        key=lambda player: (position_priority.get(player["position"], 5), player["id"])
    )
    return sorted_XI

def get_last_5_matches(match_id, is_home):
    matches = db.executeQuery(GET_LAST_5_MATCHES_QUERY, params=(match_id,is_home))

    results = [{'match_id': row[0], 'date': row[1], 'result': (row[2] == "WIN"),
                     'home_id': row[3], 'away_id': row[4], 'home_goals': row[5], 'away_goals': row[6]} 
                    for row in (matches)]

    return results

def get_ht_ft(home_goals, away_goals):
    ht_home = sum(1 for g in home_goals if g["period"] == '1H')
    ht_away = sum(1 for g in away_goals if g["period"] == '1H')
    ft_home = sum(1 for g in home_goals)
    ft_away = sum(1 for g in away_goals)

    return f"(HT {ht_home}-{ht_away}) (FT {ft_home}-{ft_away})"

@match_details_bp.route('/match/<int:id>')
def match_details(id):
    match_info = get_match_info(id)

    if match_info == {}:
         return redirect(url_for('match.get_matches'))

    event_widths = calculate_metric_widths(id)
    summary_widths = event_widths[:13]
    shot_widths = event_widths[13:17]
    pass_widths = event_widths[17:20]
    def_widths = event_widths[20:]

    home_last_5 = get_last_5_matches(id,0)
    away_last_5 = get_last_5_matches(id,1)
    home_XI = get_starting_XI(id,0)
    away_XI = get_starting_XI(id,1)
    home_subs = get_substitutions(id, 0)
    away_subs = get_substitutions(id, 1)
    home_players = merge_players(home_XI, home_subs)
    away_players = merge_players(away_XI, away_subs)

    home_goals = get_goals(id,0)
    away_goals = get_goals(id,1)
    home_cards = get_cards(id, 0)
    away_cards = get_cards(id, 1)

    key_events = get_key_events(home_goals, home_subs, home_cards, away_goals, away_subs, away_cards)

    ht_ft = get_ht_ft(home_goals, away_goals)


    shots = get_shots(id, (home_goals + away_goals))
    passes = get_events(id, GET_PASSES_QUERY, 'pass')
    interceptions = get_events(id, GET_INTERCEPTIONS_QUERY, 'interception')
    offsides = get_events(id, GET_OFFSIDES_QUERY, 'offside')
    duels = get_events(id, GET_DUELS_QUERY, 'duel')
    fouls = get_events(id, GET_FOULS_QUERY, 'foul')
    freekicks = get_events(id, GET_FREEKICKS_QUERY, 'freekick')
    saves = get_events(id, GET_SAVES_QUERY, 'save')

    player_images = load_player_images((home_XI + away_XI), (home_subs + away_subs))

    return render_template('stats/match_stats.html',
                           match=match_info,
                           summary_widths=summary_widths,
                           shot_widths=shot_widths,
                           pass_widths=pass_widths,
                           def_widths=def_widths,
                           home_goals=home_goals,
                           away_goals=away_goals,
                           ht_ft=ht_ft,
                           home_last_5=home_last_5,
                           away_last_5=away_last_5,
                           home_XI=home_XI,
                           away_XI=away_XI,
                           home_players= home_players,
                           away_players= away_players,
                           player_images=player_images,
                           key_events=key_events,
                           shots= shots,
                           passes=passes,
                           interceptions=interceptions,
                           offsides=offsides,
                           duels=duels,
                           fouls=fouls,
                           freekicks=freekicks,
                           saves=saves
                           )