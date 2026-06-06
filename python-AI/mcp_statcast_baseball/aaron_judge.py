from pybaseball import playerid_lookup, statcast_batter
import pandas as pd
from datetime import date

# --- Config ---
FIRST_NAME = "Aaron"
LAST_NAME  = "Judge"
YEARS_BACK = 3

# --- Lookup player ID dynamically ---
lookup = playerid_lookup(LAST_NAME, FIRST_NAME)
if lookup.empty:
    raise ValueError(f"Player '{FIRST_NAME} {LAST_NAME}' not found.")

player    = lookup.iloc[0]
player_id = int(player['key_mlbam'])
print(f"Found: {player['name_first'].title()} {player['name_last'].title()} | MLBAM: {player_id}\n")

# --- Date range ---
end_year   = date.today().year
start_year = end_year - YEARS_BACK
start_date = f"{start_year}-03-01"
end_date   = date.today().strftime('%Y-%m-%d')

# --- Fetch Statcast ---
print(f"Fetching Statcast data ({start_date} → {end_date})...")
df = statcast_batter(start_date, end_date, player_id=player_id)
pa = df[df['events'].notna()].copy()
pa['game_date'] = pd.to_datetime(pa['game_date'])
pa['season']    = pa['game_date'].dt.year

hit_events  = ['single', 'double', 'triple', 'home_run']
ab_events   = ['single', 'double', 'triple', 'home_run',
               'strikeout', 'strikeout_double_play',
               'field_out', 'grounded_into_double_play',
               'force_out', 'double_play', 'fielders_choice',
               'fielders_choice_out', 'sac_bunt_double_play']
walk_events = ['walk', 'intent_walk']
k_events    = ['strikeout', 'strikeout_double_play']

# --- Per-season stats ---
rows = []
for season, group in pa.groupby('season'):
    s_ab  = group['events'].isin(ab_events).sum()
    s_h   = group['events'].isin(hit_events).sum()
    s_1b  = (group['events'] == 'single').sum()
    s_2b  = (group['events'] == 'double').sum()
    s_3b  = (group['events'] == 'triple').sum()
    s_hr  = (group['events'] == 'home_run').sum()
    s_bb  = group['events'].isin(walk_events).sum()
    s_k   = group['events'].isin(k_events).sum()
    s_hbp = (group['events'] == 'hit_by_pitch').sum()
    s_sf  = (group['events'] == 'sac_fly').sum()
    s_pa  = len(group)

    avg  = round(s_h / s_ab, 3)          if s_ab > 0 else 0
    obp  = round((s_h + s_bb + s_hbp) /
                 (s_ab + s_bb + s_hbp + s_sf), 3) if (s_ab + s_bb + s_hbp + s_sf) > 0 else 0
    slg  = round((s_1b + 2*s_2b + 3*s_3b + 4*s_hr) / s_ab, 3) if s_ab > 0 else 0
    ops  = round(obp + slg, 3)

    contact = group[group['launch_speed'].notna()]
    ev  = round(contact['launch_speed'].mean(), 1) if not contact.empty else 'N/A'
    xba = round(contact['estimated_ba_using_speedangle'].mean(), 3) if not contact.empty else 'N/A'

    rows.append({
        'Season': season,
        'PA'    : s_pa,
        'AB'    : int(s_ab),
        'H'     : int(s_h),
        '2B'    : int(s_2b),
        '3B'    : int(s_3b),
        'HR'    : int(s_hr),
        'BB'    : int(s_bb),
        'K'     : int(s_k),
        'AVG'   : avg,
        'OBP'   : obp,
        'SLG'   : slg,
        'OPS'   : ops,
        'EV'    : ev,
        'xBA'   : xba,
    })

# --- Print table ---
print(f"\n{'='*105}")
print(f"  {FIRST_NAME} {LAST_NAME} — Last {YEARS_BACK} Seasons (Statcast)")
print(f"{'='*105}")
print(f"{'Season':<8} {'PA':>5} {'AB':>5} {'H':>5} {'2B':>4} {'3B':>4} {'HR':>5} "
      f"{'BB':>5} {'K':>5} {'AVG':>6} {'OBP':>6} {'SLG':>6} {'OPS':>6} {'EV':>6} {'xBA':>6}")
print(f"{'-'*105}")

for r in rows:
    print(
        f"{r['Season']:<8} "
        f"{r['PA']:>5} "
        f"{r['AB']:>5} "
        f"{r['H']:>5} "
        f"{r['2B']:>4} "
        f"{r['3B']:>4} "
        f"{r['HR']:>5} "
        f"{r['BB']:>5} "
        f"{r['K']:>5} "
        f"{r['AVG']:>6} "
        f"{r['OBP']:>6} "
        f"{r['SLG']:>6} "
        f"{r['OPS']:>6} "
        f"{r['EV']:>6} "
        f"{r['xBA']:>6}"
    )

# --- Overall contact quality ---
all_contact = pa[pa['launch_speed'].notna()]
print(f"\n--- Quality of Contact ({start_year}–present) ---")
print(f"Avg Exit Velocity : {all_contact['launch_speed'].mean():.1f} mph")
print(f"Avg Launch Angle  : {all_contact['launch_angle'].mean():.1f}°")
print(f"Avg xBA           : {all_contact['estimated_ba_using_speedangle'].mean():.3f}")