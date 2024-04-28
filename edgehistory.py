import os
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta
import diskcache as dc
import argparse
import json
import csv

DEFAULT_DB_PATH = os.path.expanduser('~/Library/Application Support/Microsoft Edge/Default/History')

class EdgeHistory:
    def __init__(self, db_path=None, ttl=300, since=None):
        self.cache = dc.Cache('./tmp/')
        self.db_path = db_path if db_path else DEFAULT_DB_PATH
        self.ttl = ttl
        self.since = since if since else datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

    def load_history(self):
        history = self.cache.get('edge_history')
        if history is not None:
            return history

        local_db_path = './tmp/History'
        shutil.copy(self.db_path, local_db_path)
        history = self.query_history(local_db_path)
        self.cache.set('edge_history', history, expire=self.ttl)
        os.remove(local_db_path)
        return history

    def query_history(self, db_path):
        query = f"""
        SELECT urls.url, urls.title, datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') AS visit_time, visits.visit_duration / 1000000.0 AS visit_duration_seconds
        FROM urls
        JOIN visits ON urls.id = visits.url
        WHERE datetime(visits.visit_time/1000000-11644473600, 'unixepoch', 'localtime') > datetime('{self.since.strftime('%Y-%m-%d %H:%M:%S')}')
        ORDER BY visits.visit_time DESC;
        """
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        columns = [column[0] for column in cur.description]
        results = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return results

    def refresh_cache(self):
        self.cache.evict('edge_history')
        return self.load_history()

    def export_results(self, results, format):
        if format == 'json':
            with open('history.json', 'w') as file:
                json.dump(results, file, indent=4)
        elif format == 'csv':
            with open('history.csv', 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        print(f"Data exported as {format}.")

    def print_results(self, results):
        for result in results:
            print(result)

def parse_args():
    parser = argparse.ArgumentParser(description='Manage and view Edge browser history.')
    parser.add_argument('--history-db', type=str, help='Path to the SQLite DB file')
    parser.add_argument('--since', type=str, help='Date time filter in the format YYYY-MM-DD or YYYY-MM-DD hh:mm')
    parser.add_argument('--ttl', type=int, help='Time to live for the cache in seconds')
    parser.add_argument('--refresh', action='store_true', help='Refresh the cache')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--csv', action='store_true', help='Output as CSV')
    parser.add_argument('--export', action='store_true', help='Export data to file')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    history = EdgeHistory(db_path=args.history_db, ttl=args.ttl, since=datetime.strptime(args.since, '%Y-%m-%d %H:%M') if args.since else None)
    result = history.refresh_cache() if args.refresh else history.load_history()

    if args.export:
        output_format = 'json' if args.json else 'csv'
        history.export_results(result, output_format)
    else:
        history.print_results(result)
