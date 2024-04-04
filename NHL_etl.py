#Imports
import json
import pandas as pd
import requests
from sqlalchemy import create_engine

# Function to acquire json file
# Referenced from https://colab.research.google.com/drive/1j37IaWSCM1EpqfM1h2kfvq2ncha_hqG8?usp=sharing#scrollTo=EEzfwD9bZxab

def get_json(url):
  try:
    response = requests.get(url, params={"Content-Type": "application/json"})
    response.raise_for_status()
  except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
    return
  except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
    return
  except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
    return
  except requests.exceptions.RequestException as err:
    print ("Other Error",err)
    return
  data = response.json()
  return data

# Function to print json data nicely
def print_json(data):
  print(json.dumps(data, indent=2))
  
# Create DF of Current Standings

url = 'https://api-web.nhle.com/v1/standings/now'
data = get_json(url)

standings_df = pd.DataFrame(data['standings'])
standings_df['date'] = pd.to_datetime(standings_df['date'])

if 'teamName' in standings_df.columns:
    standings_df['teamName'] = standings_df['teamName'].apply(lambda x: x['default'] if isinstance(x, dict) else x)
if 'teamCommonName' in standings_df.columns:
    standings_df['teamCommonName'] = standings_df['teamCommonName'].apply(lambda x: x['default'] if isinstance(x, dict) else x)
if 'teamAbbrev' in standings_df.columns:
    standings_df['teamAbbrev'] = standings_df['teamAbbrev'].apply(lambda x: x['default'] if isinstance(x, dict) else x)

# Team Abbrevs used to cycle through games
team_abbrevs = [standings_df['teamAbbrev'].unique()]

# Function to get season id based on Min Date Game
# Season ids in the format of yyyyyyyy

def set_season_id(standingsdf):
    min_date = min(standings_df['date'])
    '''
    Get the minimum date for standings
    
    The min date should be the day the notebook was run, or the end of the season.
    
    August is the turnover point, to switch to the next season.
    
    i.e seasonid = 20232024
    '''
    year = min_date.year
    if min_date.month < 8:
        season_id = f"{year-1}{year}"
    else:
        season_id = f"{year}{year+1}"
    return season_id

# Get Games from Most recent Season

season_id = set_season_id(standings_df)
game_ids = set() # Set so only contains unique IDs
print('Processing Game Ids')

for team in team_abbrevs[0]:
        url = f"https://api-web.nhle.com/v1/club-schedule-season/{team}/{season_id}"
        data = get_json(url)
        for game in data['games']:
            if game['gameState'] == 'OFF':
                if game['gameType'] in (2,3): #Only get regular season and playoffs (gametype 2 and 3 respectively)
                    id = game['id']
                    if id not in game_ids:
                        game_ids.add(id)

print(f'{len(game_ids)} Game Ids added to Game_ids')

# Get stat function will simplify getting game stats that are deeply nested in the JSON
def get_stat(teamGameStats, stat_category, is_home):
    stat_key = 'homeValue' if is_home else 'awayValue'
    for stat in teamGameStats:
        if stat['category'] == stat_category:
            return stat[stat_key]
    return None


def game_stat_extraction(gameid):
    url = f'https://api-web.nhle.com/v1/gamecenter/{gameid}/boxscore'
    boxscore = get_json(url)
    
    boxscore_df = []
    
    home = boxscore.get('homeTeam',None)
    away = boxscore.get('awayTeam', None)
    teamGameStats = boxscore['summary']['teamGameStats']
    
    game_details = {
    'gameid' : gameid,
    'game_date': boxscore['gameDate'],
    'venue': boxscore['venue']['default'],
    'gameType': boxscore['gameType'],
    'season': boxscore['season'],
    'period_count': boxscore['periodDescriptor']['number'],
    'period_type': boxscore['periodDescriptor']['periodType'],
    'home_id': home.get('id'),
    'home_abbrev': home.get('abbrev'),
    'home_goals': home.get('score'),
    'home_sog': get_stat(teamGameStats, 'sog', True),
    'home_faceoffWinningPctg': get_stat(teamGameStats, 'faceoffWinningPctg', True),
    'home_powerPlayConversion': get_stat(teamGameStats, 'powerPlay', True),
    'home_pim': get_stat(teamGameStats, 'pim', True),
    'home_hits': get_stat(teamGameStats, 'hits', True),
    'home_blocks': get_stat(teamGameStats, 'blockedShots', True),
    'away_id': away.get('id'),
    'away_abbrev': away.get('abbrev'),
    'away_goals': away.get('score', None),
    'away_sog': get_stat(teamGameStats, 'sog', False),
    'away_faceoffWinningPctg': get_stat(teamGameStats, 'faceoffWinningPctg', False),
    'away_powerPlayConversion': get_stat(teamGameStats, 'powerPlay', False),
    'away_pim': get_stat(teamGameStats, 'pim', False),
    'away_hits': get_stat(teamGameStats, 'hits', False),
    'away_blocks': get_stat(teamGameStats, 'blockedShots', False),
    }
    
    boxscore_df.append(game_details)
    boxscore_df = pd.DataFrame(boxscore_df)
    
    return boxscore_df

# For loop will iterate over all of our game ids, get their boxscore and add them to the season_boxscores dataframe


season_boxscores = pd.DataFrame()

print('Processing Boxscores')

for game_id in game_ids:
    try:
        temp_df = game_stat_extraction(game_id)
        season_boxscores = pd.concat([season_boxscores, temp_df], ignore_index=True)
    except requests.HTTPError as e:
        print(f"HTTP Error for game ID {game_id}: {e}")  # Log the error or print it
    except TypeError as e:
        print(f"TypeError encountered for game ID {game_id}: {e}")  # Handle cases where data might be None
    except Exception as e:
        print(f"Unexpected error for game ID {game_id}: {e}")
  
print(f'{len(season_boxscores)} Boxscores added to season_boxscores')
      
# season_boxscores now contains all team stats for their games played

# Get player info and game logs in seperate dfs

# Get goalie and skater ID' to later get their stats

player_ids = set()
goalie_ids = set()
season_id = set_season_id(standings_df)

for team in team_abbrevs[0]:
    url = f'https://api-web.nhle.com/v1/roster/{team}/20222023'
    try:
        data = get_json(url)

        for position_group in data.values():
            if isinstance(position_group, list):
                for player in position_group:
                    player_id = player.get('id')
                    position_code = player.get('positionCode')
                    if player_id:
                        if position_code == "G":
                            goalie_ids.add(player_id)
                        else:
                            player_ids.add(player_id)
    except requests.RequestException as e:
        print(f"Request error for team {team}: {e}")
        

# Player stats

# Initialize list, which will later be appended to the aggregated player stats df
# Player and Goalie stats will be gathered from the player landing endpoint

player_stats_list = []

print('processing player stats')

for player_id in player_ids:
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    data = get_json(url)
    
    season_stats = data['featuredStats']['regularSeason'].get('subSeason', {})
            
    season_stats_all = {
                'player_id': player_id,
                'current_team': data.get('currentTeamId',None),
                'first_name': data['firstName']['default'],
                'last_name': data['lastName']['default'],
                'position': data['position'],
                'photo': data['headshot'],
                'games_played': season_stats.get('gamesPlayed'),
                'goals': season_stats.get('goals'),
                'assists': season_stats.get('assists'),
                'points': season_stats.get('points'),
                'plus_minus': season_stats.get('plusMinus'),
                'pim': season_stats.get('pim'),
                'game_winning_goals': season_stats.get('gameWinningGoals'),
                'ot_goals': season_stats.get('otGoals'),
                'shots': season_stats.get('shots'),
                'shooting_pctg': season_stats.get('shootingPctg'),
                'power_play_goals': season_stats.get('powerPlayGoals'),
                'power_play_points': season_stats.get('powerPlayPoints'),
                'shorthanded_goals': season_stats.get('shorthandedGoals'),
                'shorthanded_points': season_stats.get('shorthandedPoints'),
            }
            
    player_stats_list.append(season_stats_all)
player_stats = pd.DataFrame(player_stats_list)

print(f'{len(player_stats)} players added to player_stats')

# Goalie Stats
goalie_stats_list = []

print('processing goalie stats')

for goalie_id in goalie_ids:
    url = f"https://api-web.nhle.com/v1/player/{goalie_id}/landing"
    data = get_json(url)

    season_stats = data['featuredStats']['regularSeason'].get('subSeason', {})
            
    season_stats_all = {
        'goalie_id': goalie_id,
        'current_team': data.get('currentTeamId',None),
        'first_name': data['firstName']['default'],
        'last_name': data['lastName']['default'],
        'position': data['position'],
        'photo': data['headshot'],
        'games_played': season_stats.get('gamesPlayed'),
        'wins': season_stats.get('wins'),
        'losses': season_stats.get('losses'),
        'ties': season_stats.get('ties'),
        'otLosses': season_stats.get('otLosses'),
        'shutouts': season_stats.get('shutouts'),
        'goalsAgainstAvg': season_stats.get('goalsAgainstAvg'),
        'savePctg': season_stats.get('savePctg')
            }
            
    goalie_stats_list.append(season_stats_all)
            
goalie_stats = pd.DataFrame(goalie_stats_list)

print(f'{len(goalie_stats)} goalies added to goalie_stats')

# Correcting formatting issue with object dtypes and the column placeName in standings_df

for col in standings_df.select_dtypes(include=['object']).columns:
    standings_df[col] = standings_df[col].apply(lambda x: x.strip().replace(r'[^\x00-\x7F]+', '') if isinstance(x, str) else json.dumps(x))

standings_df['placeName'] = standings_df['placeName'].apply(lambda x: json.loads(x)['default'] if isinstance(x, str) else x)

# Create connection to Database.

db_config = {
    "username": "root",
    "password": "root",
    "host": "localhost",
    "port": 3306,
    "database": "nhl"
}
connection_string = f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(connection_string)

'''
TABLES TO BE UPLOADED

Standings = standings_df
Boxscores = season_boxscores
Players = player_stats
Goalies = goalie_stats

'''
# Upload and append to tables

standings_df.to_sql('standings', con=engine, index=False, if_exists='replace')
season_boxscores.to_sql('boxscores', con=engine, index=False, if_exists='replace')
player_stats.to_sql('players', con=engine, index=False, if_exists='replace')
goalie_stats.to_sql('goalies', con=engine, index=False, if_exists='replace')

print('Tables Uploaded')