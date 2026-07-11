"""
World Cup Module
Powered by worldcup26.ir
"""
from datetime import datetime
import difflib

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

def team_lookup():
    teams_data = wc_api.get_teams()

    if teams_data.get("error"):
        return {}

    lookup = {}

    for team in teams_data.get("teams", []):
        lookup[str(team["id"])] = {
            "name_en": team["name_en"]
        }

    return lookup


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

def get_fixtures():
    """
    Fixtures = today's scheduled matches.
    """
    return get_today()

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


def get_group(group_name):
    data = wc_api.get_groups()

    if data.get("error"):
        return "Unable to load standings."

    groups = data.get("groups", [])

    if not groups:
        return "No standings available."

    group_name = group_name.upper()

    group = next(
        (g for g in groups if g["name"].upper() == group_name),
        None
    )

    if not group:
        return f"Group {group_name} does not exist."

    teams_data = wc_api.get_teams()

    lookup = {}

    if not teams_data.get("error"):
        for team in teams_data.get("teams", []):
            lookup[str(team["id"])] = team["name_en"]

    teams = sorted(
        group["teams"],
        key=lambda t: (
            int(t["pts"]),
            int(t["gd"]),
            int(t["gf"])
        ),
        reverse=True,
    )

    lines = [f"🏆 *Group {group_name}*", ""]

    for position, team in enumerate(teams, start=1):

        name = lookup.get(str(team["team_id"]), "Unknown")

        pts = int(team["pts"])
        suffix = "pt" if pts == 1 else "pts"

        lines.append(
            f"{position}. {name:<28} {pts} {suffix}"
        )

    return "\n".join(lines)


def get_team(team_name):
    data = wc_api.get_groups()

    if data.get("error"):
        return "Unable to load team information."

    groups = data.get("groups", [])

    if not groups:
        return "No team information available."

    lookup = team_lookup()

    # Create a name -> id mapping
    names = {}

    for team_id, info in lookup.items():
        names[info["name_en"]] = team_id

    # Try exact match first
    match = None

    for name in names:
        if name.lower() == team_name.lower():
            match = name
            break

    # If no exact match, try closest match
    if not match:
        close = difflib.get_close_matches(
            team_name,
            names.keys(),
            n=1,
            cutoff=0.5,
        )

        if close:
            match = close[0]

    if not match:
        return f"No team found for '{team_name}'."

    team_id = names[match]

    # Search every group
    for group in groups:

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

            if str(team["team_id"]) == str(team_id):

                pts = int(team["pts"])
                suffix = "pt" if pts == 1 else "pts"

                return (
                    f"🏆 *{match}*\n\n"
                    f"Group: {group['name']}\n"
                    f"Position: {position}\n"
                    f"Points: {pts} {suffix}"
                )

    return "Team not found."





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
wc group <letter>
wc team <name>
wc help"""
        ]

    elif text == "wc help":
        return [
            """🏆 *World Cup Commands*

🏆 *World Cup Commands*

wc today
wc fixtures
wc live
wc next
wc last
wc standings
wc group <letter>
wc team <name>"""
        ]
    elif text in ["wc today", "wc fixtures"]:
        return [get_fixtures()]

    elif text == "wc live":
        return [get_live()]

    elif text == "wc next":
        return [get_next()]

    elif text == "wc last":
        return [get_last()]
    
    elif text.startswith("wc group "):

        group = text.replace("wc group ", "").strip()

        return [get_group(group)]

    elif text.startswith("wc team "):

        team = text.replace("wc team ", "").strip()

        return [get_team(team)]

    elif text == "wc standings":

        return [get_standings()]
        

    return [
        "Unknown World Cup command.\n\nType *wc help*."
    ]