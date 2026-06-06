# MLB Statcast MCP Server

A local MCP (Model Context Protocol) server that connects Claude Code to MLB Statcast data. Ask Claude natural language questions about any MLB batter and get real stats pulled live from Baseball Savant.

---

## What You Can Ask Claude

Once set up, just talk to Claude naturally:

```
Show me Aaron Judge's stats this season
What is Judge's xBA in 2026?
How does Ohtani hit against curveballs?
Show me Ben Rice's stats
How does Judge hit against Skubal?
Give me Judge's stats for the last 3 years
What is Gunnar Henderson's OPS?
```

Claude will automatically call the right tool, fetch the data from Statcast, and return the results.

---

## How It Works

```
You (natural language)
        ↓
   Claude Code (AI)
        ↓
  MCP Server (local Python process)
        ↓
  pybaseball → Baseball Savant (Statcast)
        ↓
  Stats returned to Claude
        ↓
  Claude summarizes and responds to you
```

The MCP server runs as a local Python process. Claude Code launches it automatically and calls its tools whenever you ask a baseball question. You never interact with the server directly.

---

## Project Structure

```
baseball/
├── statcast_mcp_server.py   # The MCP server (main file)
└── README.md                # This file
```

---

## Prerequisites

- Python 3.10+
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- Git Bash installed on Windows (https://git-scm.com/downloads/win)

---

## Installation

### 1. Install Python dependencies

```bash
pip install mcp pybaseball pandas
```

### 2. Install Git Bash (Windows only)

Download and install from https://git-scm.com/downloads/win

Then set the environment variable so Claude Code can find it. Open PowerShell and run:

```powershell
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_GIT_BASH_PATH", "C:\Users\<YourUsername>\Documents\Dev\Git\bin\bash.exe", "User")
```

Then reload it in your current session:

```powershell
$env:CLAUDE_CODE_GIT_BASH_PATH = "C:\Users\<YourUsername>\Documents\Dev\Git\bin\bash.exe"
```

> Replace `<YourUsername>` with your actual Windows username. Adjust the path if Git installed somewhere different.

### 3. Register the MCP server with Claude Code

Run this once in your terminal:

```bash
claude mcp add statcast python "C:\Users\<YourUsername>\Dev\repos\public\python-AI\baseball\statcast_mcp_server.py"
```

Verify it was added:

```bash
claude mcp list
```

---

## Running Claude Code

Open a terminal (PowerShell or Git Bash) and run:

```bash
claude
```

That's it. Claude Code will automatically start the MCP server in the background.

To confirm the statcast server is connected, type this inside the Claude Code session:

```
/mcp
```

You should see the statcast server listed with its 5 tools.

---

## Available Tools

Claude selects the right tool automatically based on your question. For reference, these are the tools running under the hood:

| Tool | What it does | Example question |
|---|---|---|
| `get_batter_season_stats` | Full season stats: PA, AB, H, HR, BB, K, AVG, OBP, SLG, OPS, exit velo, xBA | "Show me Judge's 2026 stats" |
| `get_batter_xba` | Quality of contact: xBA, exit velo, launch angle, hard-hit rate, barrel rate | "What's Judge's xBA this year?" |
| `get_batter_pitch_type_stats` | Stats vs a specific pitch type + whiff rate | "How does Ohtani hit curveballs?" |
| `get_batter_vs_pitcher` | Head-to-head matchup stats + pitch mix seen | "How does Judge hit against Skubal?" |
| `get_batter_multi_season` | Year-by-year breakdown for the last N seasons | "Show me Judge's stats the last 3 years" |

---

## Stats Glossary

| Stat | Definition |
|---|---|
| PA | Plate appearances |
| AB | At bats |
| AVG | Batting average (H / AB) |
| OBP | On-base percentage |
| SLG | Slugging percentage |
| OPS | OBP + SLG |
| xBA | Expected batting average based on exit velocity and launch angle |
| EV | Average exit velocity (mph) |
| Hard-Hit Rate | % of balls hit 95+ mph |
| Barrel Rate | % of balls hit with optimal exit velo + launch angle combo |
| Whiff Rate | Swings and misses / total swings on a given pitch type |

---

## Notes

- **First query is slow** — pybaseball scrapes Baseball Savant live, so the first request for any player takes 30–60 seconds. Repeat questions about the same player in the same session are instant due to in-session caching.
- **Data source** — all data comes from Baseball Savant (Statcast). No FanGraphs or Baseball Reference.
- **Current season** — stats default to the current year if no season is specified.
- **Do not run the server manually** — Claude Code launches and manages it automatically.

---

## Troubleshooting

**`/mcp` shows no tools or server is disconnected**
- Make sure dependencies are installed: `pip install mcp pybaseball pandas`
- Verify the file path in your MCP config is correct: `claude mcp get statcast`
- Re-add the server if needed: `claude mcp remove statcast` then `claude mcp add ...`

**Slow responses**
- Normal on first query per player. Statcast scrapes take 30–60 seconds.

**Player not found**
- Try alternate spellings (e.g. "Shohei" not "Ohtani" alone — first and last name are separate fields passed by Claude)

**Git Bash / PATH errors on Windows**
- Make sure `CLAUDE_CODE_GIT_BASH_PATH` is set and points to a real `bash.exe`
- Open a new terminal after setting the environment variable


**coding tips**
@lru_cache on the Statcast fetch so asking two questions about the same player in a session doesn't scrape twice
Plain English pitch types ("curveball", "slider", etc.) are mapped to Statcast pitch codes internally so Claude can pass them through naturally
Graceful errors — every tool returns {"error": "..."} instead of crashing if a player isn't found or has no data