"""
World Cup Module
Powered by worldcup26.ir
"""

from datetime import datetime

import wc_api

MAX_MESSAGE_LENGTH = 1500


def split_message(text):
    """
    Split long WhatsApp messages into chunks.
    """
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]

    parts = []

    while len(text) > MAX_MESSAGE_LENGTH:
        split_at = text.rfind("\n", 0, MAX_MESSAGE_LENGTH)

        if split_at == -1:
            split_at = MAX_MESSAGE_LENGTH

        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    if text:
        parts.append(text)

    return parts


def parse_match_date(date_string):
    try:
        return datetime.strptime(date_string, "%m/%d/%Y %H:%M")
    except Exception:
        return None
    

def get_status(game):
    finished = str(game.get("finished", "")).upper()
    elapsed = str(game.get("time_elapsed", "")).lower()

    if finished == "TRUE":
        return "FT"

    if elapsed in ["", "null", "none", "notstarted"]:
        dt = parse_match_date(game["local_date"])
        return dt.strftime("%H:%M") if dt else "Scheduled"

    if elapsed == "finished":
        return "FT"

    if elapsed == "live":
        return "LIVE 🔴"

    return f"{elapsed}'"


def format_match(game):
    home = game["home_team_name_en"]
    away = game["away_team_name_en"]

    home_score = str(game.get("home_score", "")).lower()
    away_score = str(game.get("away_score", "")).lower()

    status = get_status(game)

    # Match not started
    if status not in ["FT"] and (
        home_score in ["", "null", "none", "0"]
        and away_score in ["", "null", "none", "0"]
    ):
        return (
            f"{home} vs {away}\n"
            f"⏰ {status}"
        )

    return (
        f"{home} {game.get('home_score', 0)} - {game.get('away_score', 0)} {away}\n"
        f"⏰ {status}"
    )


def get_all_games():
    data = wc_api.get_games()

    if data.get("error"):
        return []

    games = data.get("games", [])

    games.sort(
        key=lambda g: parse_match_date(g["local_date"]) or datetime.max
    )

    return games


def get_today():
    today = datetime.now().date()

    games = []

    for game in get_all_games():
        dt = parse_match_date(game["local_date"])

        if dt and dt.date() == today:
            games.append(game)

    if not games:
        return "📅 No World Cup matches today."

    lines = ["📅 *Today's World Cup Matches*", ""]

    for game in games:
        lines.append(format_match(game))
        lines.append("")

    return "\n".join(lines).strip()


def get_live():
    games = []

    for game in get_all_games():

        if str(game.get("finished", "")).upper() == "TRUE":
            continue

        elapsed = str(game.get("time_elapsed", "")).lower()

        if elapsed not in ["", "null", "none", "finished", "notstarted"]:
            games.append(game)

    if not games:
        return "🔴 No live World Cup matches."

    lines = ["🔴 *Live World Cup Matches*", ""]

    for game in games:
        lines.append(format_match(game))
        lines.append("")

    return "\n".join(lines).strip()


def get_next():
    now = datetime.now()

    upcoming = []

    for game in get_all_games():

        dt = parse_match_date(game["local_date"])

        if dt and dt > now:
            upcoming.append(game)

    upcoming = sorted(
        upcoming,
        key=lambda g: parse_match_date(g["local_date"]) or datetime.max
    )
    if not upcoming:
        return "📅 No upcoming World Cup matches."

    lines = ["⏭️ *Next World Cup Matches*", ""]

    for game in upcoming[:5]:
        lines.append(format_match(game))
        lines.append("")

    return "\n".join(lines).strip()


def get_last():
    now = datetime.now()

    finished = []

    for game in get_all_games():

        dt = parse_match_date(game["local_date"])

        if dt and dt < now:
            finished.append(game)

    finished = sorted(
        finished,
        key=lambda g: parse_match_date(g["local_date"]) or datetime.min,
        reverse=True,
    )

    if not finished:
        return "🏁 No completed World Cup matches."

    lines = ["🏁 *Latest World Cup Results*", ""]

    for game in finished[:5]:
        lines.append(format_match(game))
        lines.append("")

    return "\n".join(lines).strip()


def get_standings():
    data = wc_api.get_groups()

    if data.get("error"):
        return "Unable to load standings."

    groups = data.get("groups", [])

    if not groups:
        return "No standings available."

    # Build team lookup
    teams_data = wc_api.get_teams()

    lookup = {}

    if not teams_data.get("error"):
        for team in teams_data.get("teams", []):
            lookup[str(team["id"])] = team["name_en"]

    lines = ["🏆 *World Cup Group Standings*", ""]

    groups = sorted(groups, key=lambda g: g["name"])
    for group in groups:

        lines.append(f"*Group {group['name']}*")

        teams = sorted(
            group["teams"],
            key=lambda t: (
                int(t["pts"]),
                int(t["gd"]),
                int(t["gf"])
            ),
            reverse=True,
        )

        for position, team in enumerate(teams, start=1):

            name = lookup.get(
                str(team["team_id"]),
                "Unknown"
            )

            pts = int(team["pts"])

            suffix = "pt" if pts == 1 else "pts"

            lines.append(
                f"{position}. {name:<28} {pts} {suffix}"
            )

        lines.append("")

    return "\n".join(lines).strip()








def handle_command(text):
    text = text.strip().lower()

    if text in ["wc", "world cup", "worldcup"]:
        return [
            """🏆 *World Cup 2026*

Available commands:

wc today
wc live
wc next
wc last
wc standings
wc help"""
        ]

    elif text == "wc help":
        return [
            """🏆 *World Cup Commands*

wc today
wc live
wc next
wc last
wc standings"""
        ]

    elif text == "wc today":
        return [get_today()]

    elif text == "wc live":
        return [get_live()]

    elif text == "wc next":
        return [get_next()]

    elif text == "wc last":
        return [get_last()]

    elif text == "wc standings":
        return split_message(get_standings())

    return [
        "Unknown World Cup command.\n\nType *wc help*."
    ]