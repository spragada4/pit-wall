import sqlite3
import httpx
import os

BASE_URL = "https://api.jolpi.ca/ergast/f1"
DB_PATH = os.environ.get("DB_PATH", "f1.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS standings (
            season TEXT,
            position TEXT,
            driver TEXT,
            constructor TEXT,
            points TEXT,
            PRIMARY KEY (season, driver)
        )
    """
    )
    conn.commit()
    conn.close()


def fetch_standings(season: str = "current"):
    url = f"{BASE_URL}/{season}/driverStandings.json"
    resp = httpx.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    standings_list = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings_list:
        return []

    rows = []
    for entry in standings_list[0]["DriverStandings"]:
        driver = f'{entry["Driver"]["givenName"]} {entry["Driver"]["familyName"]}'
        constructor = entry["Constructors"][0]["name"]
        rows.append(
            (
                standings_list[0]["season"],
                entry["position"],
                driver,
                constructor,
                entry["points"],
            )
        )

    conn = get_connection()
    conn.executemany("INSERT OR REPLACE INTO standings VALUES (?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()
    return rows


def get_standings_from_db(season: str = "current"):
    conn = get_connection()
    query = (
        "SELECT position, driver, constructor, points "
        "FROM standings WHERE season = ? OR ? = 'current' "
        "ORDER BY CAST(position AS INTEGER)"
    )
    cur = conn.execute(query, (season, season))
    result = cur.fetchall()
    conn.close()
    return result

if __name__ == "__main__":
    init_db()
    fetch_standings()
    print("Standings fetched and stored.")
