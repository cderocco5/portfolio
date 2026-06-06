"""
Statcast MCP Server
-------------------
Tools for querying Baseball Savant / Statcast batter data.

Install:
    pip install mcp pybaseball pandas

Claude Desktop config (Windows):
    %APPDATA%\\Claude\\claude_desktop_config.json

    {
      "mcpServers": {
        "statcast": {
          "command": "python",
          "args": ["C:\\\\full\\\\path\\\\to\\\\statcast_mcp_server.py"]
        }
      }
    }
"""

import sys
import os
import io
import contextlib
import warnings
import pandas as pd
from datetime import date
from mcp.server.fastmcp import FastMCP

# Suppress pybaseball warnings/deprecations
warnings.filterwarnings("ignore")
os.environ["PYBASEBALL_CACHE"] = "false"

# ---------------------------------------------------------------------------
# Stdout suppression context manager
# MCP owns stdout for JSON-RPC — silence pybaseball prints without
# replacing sys.stdout globally (which breaks MCP's buffer access).
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def _silence():
    """Redirect stdout to stderr only for the duration of the block."""
    old = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old

# Import pybaseball inside silence so its module-level prints are swallowed
with _silence():
    from pybaseball import playerid_lookup, statcast_batter

mcp = FastMCP("statcast")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PITCH_TYPE_MAP = {
    "fastball"   : ["FF", "SI", "FC"],
    "sinker"     : ["SI"],
    "cutter"     : ["FC"],
    "curveball"  : ["CU", "KC"],
    "slider"     : ["SL", "ST", "SV"],
    "changeup"   : ["CH", "FS"],
    "splitter"   : ["FS"],
    "knuckleball": ["KN"],
    "sweeper"    : ["ST"],
}

HIT_EVENTS  = ["single", "double", "triple", "home_run"]
AB_EVENTS   = ["single", "double", "triple", "home_run",
               "strikeout", "strikeout_double_play",
               "field_out", "grounded_into_double_play",
               "force_out", "double_play", "fielders_choice",
               "fielders_choice_out", "sac_bunt_double_play"]
WALK_EVENTS = ["walk", "intent_walk"]
K_EVENTS    = ["strikeout", "strikeout_double_play"]

_cache: dict = {}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_player(first: str, last: str) -> tuple:
    with _silence():
        result = playerid_lookup(last, first)
    if result.empty:
        raise ValueError(f"Player '{first} {last}' not found.")
    row  = result.iloc[0]
    name = f"{row['name_first'].title()} {row['name_last'].title()}"
    return int(row["key_mlbam"]), name


def fetch_statcast(player_id: int, start: str, end: str) -> pd.DataFrame:
    key = (player_id, start, end)
    if key not in _cache:
        with _silence():
            _cache[key] = statcast_batter(start, end, player_id=player_id)
    return _cache[key]


def season_dates(year: int) -> tuple:
    start = f"{year}-03-01"
    end   = min(date.today(), date(year, 11, 1)).strftime("%Y-%m-%d")
    return start, end


def compute_stats(pa: pd.DataFrame) -> dict:
    s_ab  = int(pa["events"].isin(AB_EVENTS).sum())
    s_h   = int(pa["events"].isin(HIT_EVENTS).sum())
    s_1b  = int((pa["events"] == "single").sum())
    s_2b  = int((pa["events"] == "double").sum())
    s_3b  = int((pa["events"] == "triple").sum())
    s_hr  = int((pa["events"] == "home_run").sum())
    s_bb  = int(pa["events"].isin(WALK_EVENTS).sum())
    s_k   = int(pa["events"].isin(K_EVENTS).sum())
    s_hbp = int((pa["events"] == "hit_by_pitch").sum())
    s_sf  = int((pa["events"] == "sac_fly").sum())

    avg     = round(s_h / s_ab, 3)                                 if s_ab > 0 else None
    obp_den = s_ab + s_bb + s_hbp + s_sf
    obp     = round((s_h + s_bb + s_hbp) / obp_den, 3)            if obp_den > 0 else None
    slg     = round((s_1b + 2*s_2b + 3*s_3b + 4*s_hr) / s_ab, 3) if s_ab > 0 else None
    ops     = round(obp + slg, 3) if obp is not None and slg is not None else None

    contact = pa[pa["launch_speed"].notna()]
    ev  = round(float(contact["launch_speed"].mean()), 1)                  if not contact.empty else None
    la  = round(float(contact["launch_angle"].mean()), 1)                  if not contact.empty else None
    xba = round(float(contact["estimated_ba_using_speedangle"].mean()), 3) if not contact.empty else None

    return {
        "PA": len(pa), "AB": s_ab, "H": s_h,
        "2B": s_2b, "3B": s_3b, "HR": s_hr,
        "BB": s_bb, "K": s_k,
        "AVG": avg, "OBP": obp, "SLG": slg, "OPS": ops,
        "avg_exit_velo": ev, "avg_launch_angle": la, "xBA": xba,
    }


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_batter_season_stats(first_name: str, last_name: str, season: int = 0) -> dict:
    """
    Season batting stats for any MLB batter from Statcast.
    Returns PA, AB, H, 2B, 3B, HR, BB, K, AVG, OBP, SLG, OPS, exit velo, xBA.

    Args:
        first_name: Batter's first name (e.g. "Aaron")
        last_name:  Batter's last name  (e.g. "Judge")
        season:     Year (e.g. 2025). Defaults to current year.
    """
    year = season if season else date.today().year
    start, end = season_dates(year)
    try:
        pid, name = resolve_player(first_name, last_name)
    except ValueError as e:
        return {"error": str(e)}
    try:
        df = fetch_statcast(pid, start, end)
    except Exception as e:
        return {"error": f"Statcast fetch failed: {e}"}
    pa = df[df["events"].notna()].copy()
    if pa.empty:
        return {"error": f"No data for {name} in {year}."}
    return {"player": name, "season": year, **compute_stats(pa)}


@mcp.tool()
def get_batter_pitch_type_stats(
    first_name: str,
    last_name: str,
    pitch_type: str,
    season: int = 0,
) -> dict:
    """
    Batter's stats vs a specific pitch type (curveball, slider, fastball, etc).
    Supported: fastball, sinker, cutter, curveball, slider, changeup, splitter, sweeper.

    Args:
        first_name: Batter's first name
        last_name:  Batter's last name
        pitch_type: Pitch type in plain English (e.g. "curveball")
        season:     Year. Defaults to current year.
    """
    year = season if season else date.today().year
    start, end = season_dates(year)
    try:
        pid, name = resolve_player(first_name, last_name)
    except ValueError as e:
        return {"error": str(e)}
    codes = PITCH_TYPE_MAP.get(pitch_type.lower().strip())
    if not codes:
        return {"error": f"Unknown pitch type '{pitch_type}'. Valid: {', '.join(PITCH_TYPE_MAP)}"}
    try:
        df = fetch_statcast(pid, start, end)
    except Exception as e:
        return {"error": f"Statcast fetch failed: {e}"}

    all_pitches = df[df["pitch_type"].isin(codes)]
    pa          = all_pitches[all_pitches["events"].notna()].copy()
    if pa.empty:
        return {"error": f"No PA data vs {pitch_type} for {name} in {year}."}

    swings = all_pitches[all_pitches["description"].isin([
        "swinging_strike", "swinging_strike_blocked", "foul", "foul_tip",
        "hit_into_play", "hit_into_play_no_out", "hit_into_play_score"
    ])]
    whiffs     = all_pitches[all_pitches["description"].isin(
        ["swinging_strike", "swinging_strike_blocked"]
    )]
    whiff_rate = round(len(whiffs) / len(swings), 3) if len(swings) > 0 else None

    return {
        "player": name, "season": year, "pitch_type": pitch_type,
        "pitches_seen": len(all_pitches), "whiff_rate": whiff_rate,
        **compute_stats(pa),
    }


@mcp.tool()
def get_batter_vs_pitcher(
    batter_first: str,
    batter_last: str,
    pitcher_first: str,
    pitcher_last: str,
    start_season: int = 2020,
    end_season: int = 0,
) -> dict:
    """
    Batter's stats against a specific pitcher across multiple seasons.

    Args:
        batter_first:  Batter's first name
        batter_last:   Batter's last name
        pitcher_first: Pitcher's first name
        pitcher_last:  Pitcher's last name
        start_season:  First season to include (default 2020)
        end_season:    Last season to include (default current year)
    """
    end_yr = end_season if end_season else date.today().year
    start  = f"{start_season}-03-01"
    end    = date.today().strftime("%Y-%m-%d")
    try:
        bid, bname = resolve_player(batter_first, batter_last)
    except ValueError as e:
        return {"error": str(e)}
    with _silence():
        p_row = playerid_lookup(pitcher_last, pitcher_first)
    if p_row.empty:
        return {"error": f"Pitcher '{pitcher_first} {pitcher_last}' not found."}
    pid   = int(p_row.iloc[0]["key_mlbam"])
    pname = f"{p_row.iloc[0]['name_first'].title()} {p_row.iloc[0]['name_last'].title()}"
    try:
        df = fetch_statcast(bid, start, end)
    except Exception as e:
        return {"error": f"Statcast fetch failed: {e}"}
    matchup = df[df["pitcher"] == pid]
    pa      = matchup[matchup["events"].notna()].copy()
    if pa.empty:
        return {"error": f"No matchup data: {bname} vs {pname} ({start_season}–{end_yr})."}
    return {
        "batter": bname, "pitcher": pname,
        "seasons": f"{start_season}–{end_yr}",
        "pitches_seen": len(matchup),
        "pitch_mix": matchup["pitch_type"].value_counts().to_dict(),
        **compute_stats(pa),
    }


@mcp.tool()
def get_batter_xba(first_name: str, last_name: str, season: int = 0) -> dict:
    """
    xBA and quality-of-contact: exit velo, launch angle, hard-hit rate, barrel rate, xBA.

    Args:
        first_name: Batter's first name
        last_name:  Batter's last name
        season:     Year. Defaults to current year.
    """
    year = season if season else date.today().year
    start, end = season_dates(year)
    try:
        pid, name = resolve_player(first_name, last_name)
    except ValueError as e:
        return {"error": str(e)}
    try:
        df = fetch_statcast(pid, start, end)
    except Exception as e:
        return {"error": f"Statcast fetch failed: {e}"}
    contact = df[df["launch_speed"].notna()].copy()
    if contact.empty:
        return {"error": f"No contact data for {name} in {year}."}
    hard_hit = contact[contact["launch_speed"] >= 95]
    barrel   = contact[
        (contact["launch_speed"] >= 98) & (contact["launch_angle"].between(26, 30))
    ]
    return {
        "player"          : name,
        "season"          : year,
        "balls_in_play"   : len(contact),
        "avg_exit_velo"   : round(float(contact["launch_speed"].mean()), 1),
        "max_exit_velo"   : round(float(contact["launch_speed"].max()), 1),
        "avg_launch_angle": round(float(contact["launch_angle"].mean()), 1),
        "hard_hit_rate"   : round(len(hard_hit) / len(contact), 3),
        "barrel_rate"     : round(len(barrel) / len(contact), 3),
        "xBA"             : round(float(contact["estimated_ba_using_speedangle"].mean()), 3),
    }


@mcp.tool()
def get_batter_multi_season(first_name: str, last_name: str, years_back: int = 3) -> dict:
    """
    Year-by-year batting stats for the past N seasons.

    Args:
        first_name: Batter's first name
        last_name:  Batter's last name
        years_back: How many seasons to go back (default 3)
    """
    try:
        pid, name = resolve_player(first_name, last_name)
    except ValueError as e:
        return {"error": str(e)}
    end_year   = date.today().year
    start_year = end_year - years_back
    try:
        df = fetch_statcast(pid, f"{start_year}-03-01", date.today().strftime("%Y-%m-%d"))
    except Exception as e:
        return {"error": f"Statcast fetch failed: {e}"}
    pa = df[df["events"].notna()].copy()
    pa["game_date"] = pd.to_datetime(pa["game_date"])
    pa["season"]    = pa["game_date"].dt.year
    return {
        "player" : name,
        "seasons": {int(s): compute_stats(g) for s, g in pa.groupby("season")},
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
