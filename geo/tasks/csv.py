import csv
from cassandra.cqlengine.query import BatchQuery
from dateutil import parser

from geo import create_celery_app
from ..model import Point

celery = create_celery_app()


@celery.task()
def parse_csv(filepath, username, trip):
    """
    Parse a csv and import to database
    """
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile.read().split('\n'))
        i = 0
        with BatchQuery() as b:
            for i, line in enumerate(reader):
                try:
                    pt = {'coord': [line['lat'], line['lon']],
                          'accurracy': line['accuracy'],
                          'username': username,
                          'created_at': parser.parse(line['time']),
                          'trip_id': trip}
                    Point.batch(b).create(**pt)
                except ValueError:
                    continue
        return i