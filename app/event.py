from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from auth import isAdmin, loginRequired

event_bp = Blueprint('event', __name__, template_folder="templates")

@event_bp.route('/')
@loginRequired
def get_events():
    """Fetches and displays a list of all events with optional filters."""
    try:
        club_id = request.args.get('club')
        date_from = request.args.get('date_from') 
        date_to = request.args.get('date_to') 
        player_name = request.args.get('player_name')
        match_period = request.args.get('match_period')
        event_sec_start = request.args.get('event_sec_start', type=float)
        event_sec_end = request.args.get('event_sec_end', type=float)
        event_name = request.args.get('event_name')
        action = request.args.get('action')
        modifier = request.args.get('modifier')
        x_begin_start = request.args.get('x_begin_start', type=float)
        x_begin_end = request.args.get('x_begin_end', type=float)
        y_begin_start = request.args.get('y_begin_start', type=float)
        y_begin_end = request.args.get('y_begin_end', type=float)
        x_end_start = request.args.get('x_end_start', type=float)
        x_end_end = request.args.get('x_end_end', type=float)
        y_end_start = request.args.get('y_end_start', type=float)
        y_end_end = request.args.get('y_end_end', type=float)
        is_success = request.args.get('is_success')

        # Temel sorgu
        query = """
        SELECT e.id, c.name AS club_name, f.dateutc AS match_date, 
               p.firstname || ' ' || p.lastname AS player_name,
               e.matchperiod, e.eventsec, e.eventname, e.action, e.modifier,
               e.x_begin, e.y_begin, e.x_end, e.y_end, e.is_success
        FROM football_match_event e
        LEFT JOIN club c ON e.club_id = c.id
        LEFT JOIN football_match f ON e.football_match_id = f.id
        LEFT JOIN player p ON e.player_id = p.id
        WHERE 1=1
        """
        params = []
        if club_id:
            query += " AND c.id = %s"
            params.append(club_id)
        if date_from:
            query += " AND f.dateutc >= %s"
            params.append(date_from)
        if date_to:
            query += " AND f.dateutc <= %s"
            params.append(date_to)
        if player_name:
            query += " AND LOWER(p.firstname || ' ' || p.lastname) LIKE %s"
            params.append(f"%{player_name.lower()}%")
        if match_period:
            query += " AND e.matchperiod = %s"
            params.append(match_period)
        if event_sec_start is not None:
            query += " AND e.eventsec >= %s"
            params.append(event_sec_start)
        if event_sec_end is not None:
            query += " AND e.eventsec <= %s"
            params.append(event_sec_end)
        if event_name:
            query += " AND e.eventname = %s"
            params.append(event_name)
        if action:
            query += " AND e.action = %s"
            params.append(action)
        if modifier:
            query += " AND e.modifier = %s"
            params.append(modifier)
        if x_begin_start is not None:
            query += " AND e.x_begin >= %s"
            params.append(x_begin_start)
        if x_begin_end is not None:
            query += " AND e.x_begin <= %s"
            params.append(x_begin_end)
        if y_begin_start is not None:
            query += " AND e.y_begin >= %s"
            params.append(y_begin_start)
        if y_begin_end is not None:
            query += " AND e.y_begin <= %s"
            params.append(y_begin_end)
        if x_end_start is not None:
            query += " AND e.x_end >= %s"
            params.append(x_end_start)
        if x_end_end is not None:
            query += " AND e.x_end <= %s"
            params.append(x_end_end)
        if y_end_start is not None:
            query += " AND e.y_end >= %s"
            params.append(y_end_start)
        if y_end_end is not None:
            query += " AND e.y_end <= %s"
            params.append(y_end_end)
        if is_success in ["0", "1"]:
            query += " AND e.is_success = %s"
            params.append(is_success)

        query += " ORDER BY f.dateutc DESC, e.eventsec ASC LIMIT 100;"
        events = db.executeQuery(query, params)

        event_names = [row[0] for row in db.executeQuery("SELECT DISTINCT eventname FROM football_match_event")]
        actions = [row[0] for row in db.executeQuery("SELECT DISTINCT action FROM football_match_event WHERE action IS NOT NULL")]
        modifiers = [row[0] for row in db.executeQuery("SELECT DISTINCT modifier FROM football_match_event WHERE modifier IS NOT NULL")]

        clubs = [{"id": row[0], "name": row[1]} for row in db.executeQuery("SELECT id, name FROM club ORDER BY name;")]
        events = [
            {
                "id": event[0],
                "club_name": event[1],
                "match_date": event[2],
                "player_name": event[3],
                "matchperiod": event[4],
                "eventsec": event[5],
                "eventname": event[6],
                "action": event[7],
                "modifier": event[8],
                "x_begin": event[9],
                "y_begin": event[10],
                "x_end": event[11],
                "y_end": event[12],
                "is_success": event[13],
            }
            for event in events
        ]
        
        return render_template('event/index.html', events=events, clubs=clubs, event_names=event_names, actions=actions, modifiers=modifiers, filters=request.args)

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('event.get_events'))

@event_bp.route('/<int:id>')
@loginRequired
def get_event(id):
    try:
        query = """
        SELECT c.name AS club_name, f.dateutc AS match_date, 
               p.firstname || ' ' || p.lastname AS player_name,
               e.matchperiod, e.eventsec, e.eventname, e.action, e.modifier,
               e.x_begin, e.y_begin, e.x_end, e.y_end, e.is_success
        FROM football_match_event e
        LEFT JOIN club c ON e.club_id = c.id
        LEFT JOIN football_match f ON e.football_match_id = f.id
        LEFT JOIN player p ON e.player_id = p.id
        WHERE e.id = %s;
        """
        event_data = db.executeQuery(query, params=(id,))
        if not event_data:
            flash(f"Event with ID {id} not found.", 'danger')
            return redirect(url_for('event.get_events'))

        event = {
            "club_name": event_data[0][0],
            "match_date": event_data[0][1],
            "player_name": event_data[0][2],
            "matchperiod": event_data[0][3],
            "eventsec": event_data[0][4],
            "eventname": event_data[0][5],
            "action": event_data[0][6],
            "modifier": event_data[0][7],
            "x_begin": event_data[0][8],
            "y_begin": event_data[0][9],
            "x_end": event_data[0][10],
            "y_end": event_data[0][11],
            "is_success": event_data[0][12],
        }
    except Exception as e:
        print(f"Error fetching event details: {e}")
        flash("Error fetching event details.", "danger")
        return redirect(url_for('event.get_events'))
    return render_template('event/details.html', event=event)

@event_bp.route('/add', methods=['GET', 'POST'])
@isAdmin
def add_event():
    """Adds a new event."""
    if request.method == 'POST':
        try:
            club_id = request.form['club_id']
            football_match_id = request.form['football_match_id']
            player_id = request.form['player_id']
            matchperiod = request.form['matchperiod']
            eventsec = request.form['eventsec']
            eventname = request.form['eventname']
            action = request.form['action']
            modifier = request.form['modifier']
            x_begin = request.form['x_begin']
            y_begin = request.form['y_begin']
            x_end = float(request.form['x_end'])
            y_end = float(request.form['y_end'])
            is_success = request.form.get('is_success') == 'on'

            query = """
            INSERT INTO football_match_event (club_id, football_match_id, player_id, matchperiod, eventsec,
                                              eventname, action, modifier, x_begin, y_begin, x_end, y_end, is_success)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            db.executeQuery(query, params=(club_id, football_match_id, player_id, matchperiod, eventsec,
                                           eventname, action, modifier, x_begin, y_begin, x_end, y_end, is_success), commit=1)
            flash('Event added successfully!', 'success')
            return redirect(url_for('event.get_events'))
        except Exception as e:
            print(f"Error adding event: {e}")
            flash('Error adding event. Please try again.', 'danger')

    clubs = db.executeQuery("SELECT id, name FROM club ORDER BY name;")
    matches = db.executeQuery("SELECT id, dateutc FROM football_match ORDER BY dateutc DESC;")
    players = db.executeQuery("SELECT id, firstname || ' ' || lastname AS fullname FROM player ORDER BY firstname;")
    return render_template('event/add.html', clubs=clubs, matches=matches, players=players)

@event_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@isAdmin
def edit_event(id):
    """Edits an existing event."""
    if request.method == 'POST':
        try:
            club_id = request.form['club_id']
            football_match_id = request.form['football_match_id']
            player_id = request.form['player_id']
            matchperiod = request.form['matchperiod']
            eventsec = request.form['eventsec']
            eventname = request.form['eventname']
            action = request.form['action']
            modifier = request.form['modifier']
            x_begin = request.form['x_begin']
            y_begin = request.form['y_begin']
            x_end = float(request.form['x_end'])
            y_end = float(request.form['y_end'])
            is_success = request.form.get('is_success') == 'on'

            query = """
            UPDATE football_match_event
            SET club_id = %s, football_match_id = %s, player_id = %s, matchperiod = %s, eventsec = %s,
                eventname = %s, action = %s, modifier = %s, x_begin = %s, y_begin = %s, x_end = %s, y_end = %s, is_success = %s
            WHERE id = %s;
            """
            db.executeQuery(query, params=(club_id, football_match_id, player_id, matchperiod, eventsec, eventname,
                                           action, modifier, x_begin, y_begin, x_end, y_end, is_success, id), commit=1)
            flash('Event updated successfully!', 'success')
            return redirect(url_for('event.get_events'))
        except Exception as e:
            print(f"Error updating event: {e}")
            flash('Error updating event. Please try again.', 'danger')
    else:
        event_query = """
        SELECT * FROM football_match_event WHERE id = %s;
        """
        event_data = db.executeQuery(event_query, params=(id,))
        if not event_data:
            flash(f"Event with ID {id} not found.", 'danger')
            return redirect(url_for('event.get_events'))

        event = {
            "id": event_data[0][0],
            "club_id": event_data[0][1],
            "football_match_id": event_data[0][2],
            "player_id": event_data[0][3],
            "matchperiod": event_data[0][4],
            "eventsec": round(event_data[0][5],2),
            "eventname": event_data[0][6],
            "action": event_data[0][7],
            "modifier": event_data[0][8],
            "x_begin": event_data[0][9],
            "y_begin": event_data[0][10],
            "x_end": event_data[0][11],
            "y_end": event_data[0][12],
            "is_success": event_data[0][13],
        }
        clubs = db.executeQuery("SELECT id, name FROM club ORDER BY name;")
        matches = db.executeQuery("SELECT id, dateutc FROM football_match ORDER BY dateutc DESC;")
        players = db.executeQuery("SELECT id, firstname || ' ' || lastname AS fullname FROM player ORDER BY firstname;")
        return render_template('event/edit.html', event=event, clubs=clubs, matches=matches, players=players)

@event_bp.route('/delete/<int:id>', methods=['POST'])
@isAdmin
def delete_event(id):
    """Deletes an event."""
    try:
        query = "DELETE FROM football_match_event WHERE id = %s;"
        db.executeQuery(query, params=(id,), commit=1)
        flash('Event deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting event: {e}")
        flash('Error deleting event. Please try again.', 'danger')
    return redirect(url_for('event.get_events'))
