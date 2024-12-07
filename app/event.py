from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db

event_bp = Blueprint('event', __name__, template_folder="templates")

@event_bp.route('/')
def get_events():
    """Fetches and displays a list of all events."""
    try:
        query = """
        SELECT e.id, c.name AS club_name, f.dateutc AS match_date, 
               p.firstname || ' ' || p.lastname AS player_name,
               e.matchperiod, e.eventsec, e.eventname, e.action, e.modifier,
               e.x_begin, e.y_begin, e.x_end, e.y_end, e.is_success
        FROM football_match_event e
        LEFT JOIN club c ON e.club_id = c.id
        LEFT JOIN football_match f ON e.football_match_id = f.id
        LEFT JOIN player p ON e.player_id = p.id
        ORDER BY f.dateutc DESC, e.eventsec ASC
        LIMIT 100;
        """
        events = db.executeQuery(query)
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
    except Exception as e:
        events = []
        print(f"Error fetching events: {e}")
    return render_template('event/index.html', events=events)

@event_bp.route('/<int:id>')
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
            "eventsec": event_data[0][5],
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
