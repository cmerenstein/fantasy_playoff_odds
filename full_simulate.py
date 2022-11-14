import pandas as pd
import numpy as np
from yahoo_oauth import OAuth2
import json
from json import dumps
import datetime
import random
import pickle 


global N_TEAMS
N_TEAMS = 10

class Yahoo_Api():
    def __init__(self, consumer_key, consumer_secret,
                access_key):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_key = access_key
        self._authorization = None
    def _login(self):
        global oauth
        oauth = OAuth2(None, None, from_file='./auth/oauth2yahoo.json')
        if not oauth.token_is_valid():
            oauth.refresh_access_token()
    # Yahoo Keys


## This function takes the big game json that the API returns and gets out the team and the points
def get_teams(game):
  team_0 = game["matchup"]["0"]["teams"]["0"]["team"][0][1]["team_id"]
  team_1 = game["matchup"]["0"]["teams"]["1"]["team"][0][1]["team_id"]
  team_points_0 = game["matchup"]["0"]["teams"]["0"]["team"][1]["team_points"]["total"]
  team_points_1 = game["matchup"]["0"]["teams"]["1"]["team"][1]["team_points"]["total"]
  return team_0, team_1, team_points_0, team_points_1

## function to get the whole schedule, so when we're simulating we don't have to re-run every time
def get_schedule(game_key, league_id):
  schedule = []
  for week in range(1, 16):
    matchups = []
#
#   We get the API call here
    yahoo_api._login()
    url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/scoreboard;week='+str(week)
    response = oauth.session.get(url, params={'format': 'json'})
#
#   ## There are 5 matchups per week
    for matchup in [str(x) for x in range( int(N_TEAMS / 2))]:
      game = response.json()['fantasy_content']['league'][1]['scoreboard']['0']['matchups'][matchup]
      team_0, team_1, pts_0, pts_1 = get_teams(game)
      matchups.append( [team_0, team_1] ) ## add matchup pair to matchup list
#
    schedule.append(matchups) ## add this week's matchups to schedule
  return schedule 

def get_completed_games(game_key, league_id):
  '''
    Get the cumulative wins and cumulative points for every week that has been played.
    Output will be list of lists, 15 weeks long, 8 teams in each list.
  '''
  # Cumulative wins and points at each week
  c_wins = [[0] * N_TEAMS] * 15
  c_points = [[0] * N_TEAMS] * 15
  #
  for week in range(1, 16): #latest_week):
  #
    week_index = week - 1
    yahoo_api._login()
    url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+game_key+'.l.'+league_id+'/scoreboard;week='+str(week)
    response = oauth.session.get(url, params={'format': 'json'})
  #
  #   set up the empty wins and points list for this week
    wins = [0] * N_TEAMS
    points = [0] * N_TEAMS
    if week_index > 0:
      wins = c_wins[week_index - 1].copy()
      points = c_points[week_index - 1].copy()
  #
    for matchup in [str(x) for x in range( int(N_TEAMS /2) )]:
      game = response.json()['fantasy_content']['league'][1]['scoreboard']['0']['matchups'][matchup]
      team_0, team_1, pts_0, pts_1 = get_teams(game)
      print("week ", week)
      print(team_0, team_1, pts_0, pts_1)
  #
      winner = 99
      if float(pts_0) > float(pts_1):
        winner = team_0
      elif float(pts_0) < float(pts_1):
        winner = team_1
  #
      try:   
        wins[int(winner) - 1] += 1
      except IndexError:
        pass
  #        
      points[int(team_0) - 1] += int(float(pts_0))
      points[int(team_1) - 1] += int(float(pts_1))
  #
    c_wins[week_index] = wins
    c_points[week_index] = points 
#
  return c_wins, c_points


def get_last_game(c_wins):
  '''
    Figure out which game was the last complete one, using the # of current wins and day of week
  '''
  last_week_wins = [0] * N_TEAMS
  last_game = 0
  for week_index, wins in enumerate(c_wins):
    day_of_week = datetime.datetime.today().weekday()
    ## If the day is Tuesday or Wednesday, we can use this week, otherwise, use last week
    if day_of_week > 0 & day_of_week < 3:
      if wins != last_week_wins:
        last_game = week_index
    else:
      if wins != last_week_wins:
        last_game = week_index - 1
    last_week_wins = wins
  return(last_game) 

def simulate_seasons(last_game, schedule, actual_record, n_iter):
  ''' 
      Simulate the remaining games in a season and return an array of final wins.
  '''
  final_wins = []
  for i in range(n_iter):
  #
    c_wins = actual_record.copy()
#
    ## numbers get weird here, just print matchups to figure it out
    for sim_week in range(last_game, 15): ## start the week *after* the last week
      ## get matchups this week
      matchups = schedule[sim_week]
#      print(matchups)
    #
    # setup empty wins and points this week
      wins = c_wins[sim_week - 1].copy()
    #
      for matchup in matchups:
        team_0 = matchup[0]
        team_1 = matchup[1]  
    #
    #   Pick the winner with random coin toss
        winner = 99
        if random.random() <= .5:
          winner = team_0
        else:
          winner = team_1
    #
        wins[int(winner) - 1] += 1
    #
      c_wins[sim_week] = wins
  #
#    for i,x in enumerate(c_wins):
#      print(i, "(week ", str(i + 1), ") ", x)
    final_wins.append(c_wins[-1])
  return final_wins

def get_playoffs(wins):
  '''
    Given the final number of wins from each team, figure out who makes playoffs.
    First we find the cutoff (# of wins of the 4th place team), then everyone above makes it.
    To break ties, we randomly pick from teams at the cutoff.
  '''
  cutoff = sorted(wins)[-4]
  made_playoffs = np.where(np.array(wins) > cutoff)[0].tolist()
#
# now randomly chose a team at the cutoff
  bubble = np.where(np.array(wins) == cutoff)[0].tolist()
  sample_n = 4 - len(made_playoffs) ## how many more need to make it
  made_playoffs.extend( random.sample(bubble, sample_n)  )
#
  return(made_playoffs)

def playoff_odds(final_wins):
  '''
    Turn all the simulated wins into one set of playoff odds
  '''
  playoffs = [0] * N_TEAMS
  for wins in final_wins:
    teams = get_playoffs(wins)
    for team in teams:
      playoffs[team] += 1
#
  odds = (np.array(playoffs) / len(final_wins))
  return odds

## ------------- Setup Yahoo API ---------------

## Get the authentication for the Yahoo API
with open('./auth/oauth2yahoo.json') as json_yahoo_file:
    auths = json.load(json_yahoo_file)

yahoo_consumer_key = auths['consumer_key']
yahoo_consumer_secret = auths['consumer_secret']
yahoo_access_key = auths['access_token']
#yahoo_access_secret = auths['access_token_secret']
#json_yahoo_file.close()

#### Declare Yahoo, and Current Week Variable ####
global yahoo_api
yahoo_api = Yahoo_Api(yahoo_consumer_key, yahoo_consumer_secret, yahoo_access_key)#, yahoo_access_secret)

## game key and ID show what league and year
game_key = "414"
league_id = "285921"

## ------------ Run actual simulations --------

## get cumulative wins and points prior to simulatino 
c_wins, c_points = get_completed_games(game_key, league_id)

## Check that wins and points make sense
for i in range(15):
  print(i, c_wins[i], c_points[i])

## Make copy of cumulative wins for starting simulations
actual_record = c_wins.copy()

fl = open("data_2022/actual_record.pkl", 'wb') 
pickle.dump(actual_record, fl)

## Get the schedule in order to simulate the remaining games
schedule = get_schedule(game_key, league_id)

fl2 = open("data_2022/schedule.pkl", 'wb') 
pickle.dump(schedule, fl2)

## Simulate 10,000 seasons with this schedule
last_game = get_last_game(actual_record)
final_wins = simulate_seasons(last_game, schedule, actual_record, 10000)

## Get final playoff odds from these simulations
odds = playoff_odds(final_wins)

## Display using actual team names
teams = ["Caleb", "Simon", "Levi", "Traci", "Dan", "Zach", "Alex", "Carter", "Anna", "Jenni"] 
pd.DataFrame( [ teams, odds])

odds_dict = {}
for team_odds, team in zip(odds, teams):
  odds_dict[team] = str(round(team_odds * 100, 3)) + "%"
#
return json.dumps(odds_dict, indent = 2)



