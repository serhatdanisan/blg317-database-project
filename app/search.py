from flask import Blueprint, request, jsonify
from database import db

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    keywords = query.split()
    
    player_club_conditions = " AND ".join([
        "(firstname ILIKE %s OR lastname ILIKE %s)"
        for _ in keywords
    ])
    countries_stadiums_conditions = " AND ".join([
        "(country ILIKE %s OR capital_city ILIKE %s OR region ILIKE %s)"
        for _ in keywords
    ])
    stadium_conditions = " AND ".join([
        "(stadium ILIKE %s OR city ILIKE %s)"
        for _ in keywords
    ])
    
    search_query = f"""
    SELECT 'player' AS type, id, firstname || ' ' || lastname AS name 
    FROM player
    WHERE {player_club_conditions}
    UNION ALL
    SELECT 'club' AS type, id, name 
    FROM club
    WHERE name ILIKE %s
    UNION ALL
    SELECT 'country' AS type, id, country 
    FROM countries
    WHERE {countries_stadiums_conditions}
    UNION ALL
    SELECT 'stadium' AS type, id, stadium 
    FROM stadiums
    WHERE {stadium_conditions}
    LIMIT 10;
    """
    
    params = []
    for keyword in keywords:
        params.extend([f"%{keyword}%", f"%{keyword}%"]) 
    params.append(f"%{query}%")  
    for keyword in keywords:
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])  
    for keyword in keywords:
        params.extend([f"%{keyword}%", f"%{keyword}%"]) 

    try:
        results = db.executeQuery(search_query, params)
        return jsonify([{"type": row[0], "id": row[1], "name": row[2]} for row in results])
    except Exception as e:
        return jsonify({"error": str(e)})