from datetime import datetime
import json

from flask import jsonify, request, render_template, current_app
from flask import Blueprint

from .. import db
from ..model import Point


api = Blueprint('api', __name__)

API_VERSION = '1.0'


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

@api.route('/', methods=['GET'])
def status():
    return jsonify({ 'status': 200, 'version': API_VERSION })

@api.route('/points', methods=['GET'])
def points():
    ''' Retrieves points '''
    as_html = request.args.get('as_html', False, type=bool)
    start = request.args.get('start', 1, type=int)
    size = min(request.args.get('size', 10, type=int), 1000)
    results = Point.query.offset(start).limit(size).all()
    total = Point.query.count()

    # Return as html so we can see the browser profiler/code highligting
    if current_app.debug or as_html:
        data = json.dumps({'points': [point.to_json() for point in results], 'count': total},
                          default=json_serial, indent=4,  separators=(',', ': '))
        return render_template('json.html', data=data)

    return jsonify({'points': [point.to_json() for point in results],
                    'count': total})

@api.route('/points', methods=['POST'])
def new_points():
    ''' Posts points and inserts to the database '''
    points = request.json
    # Validate
    if 'points' not in points and points['points'] is list:
        return jsonify({'status': 400,
                        'message': 'Missing points list in posted json'}), 400
    points = points['points']
    for point in points:
        p = Point.from_json(point)
        db.session.add(p)
    db.session.commit()
    return jsonify({'status': 201,
                    'message': 'uploaded {} points'.format(len(points))}), 201
