import pandas as pd
import numpy as np
import random
import pickle 
import json
import math
import datetime

global N_TEAMS
N_TEAMS = 10
teams = ["Caleb", "Simon", "Levi", "Traci", "Dan", "Zach", "Alex", "Carter", "Anna", "Jenni"]

def random_winner(matchup):
  team_0 = matchup[0]
  team_1 = matchup[1]  
  #
  #   Pick the winner with random coin toss
  if random.random() <= .5:
    return team_0
  else:
    return team_1

def picked_winner(random_winner, matchup, week,  picks):
  team_0 = matchup[0]
  team_1 = matchup[1]  
  # 
  try:
    this_weeks_picks = picks[week]
    if team_0 in this_weeks_picks:
      return team_0
    elif team_1 in this_weeks_picks:
      return team_1
    else:
      return random_winner 
  except KeyError:
    return random_winner


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


def simulate_seasons(last_game, schedule, actual_record, n_iter, picks):
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
      matchups = schedule[sim_week]
    #
    # setup empty wins and points this week
      wins = c_wins[sim_week - 1].copy()
    #
      for matchup in matchups:
        winner = random_winner(matchup) ## get coin-toss winner
    #
        winner = picked_winner(winner, matchup, sim_week, picks) ## override if there's a picked winner
        wins[int(winner) - 1] += 1
    #
      c_wins[sim_week] = wins
  #
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


## ------------- Run Simulations ----------------------
def simulate(record_file = "data_2022/actual_record.pkl", schedule_file = "data_2022/schedule.pkl",
            n_iter = 10000, picks = {}):
  '''
    Main function to run the whole simulation
  '''
  fl = open(record_file, 'rb') 
  actual_record = pickle.load(fl)
#
  ## Get the schedule in order to simulate the remaining games
  fl2 = open(schedule_file, 'rb') 
  schedule = pickle.load(fl2)
#
  ## Simulate 10,000 seasons with this schedule
  last_game = get_last_game(actual_record)
  final_wins = simulate_seasons(last_game, schedule, actual_record, 10000, picks)
#
  ## Get final playoff odds from these simulations
  odds = playoff_odds(final_wins)
#
  ## Display using actual team names
  teams = ["Caleb", "Simon", "Levi", "Traci", "Dan", "Zach", "Alex", "Carter", "Anna", "Jenni"]
  print(pd.DataFrame( [ teams, odds]))
#
  ## Make json object for the results
  odds_dict = {}
  for team_odds, team in zip(odds, teams):
    odds_dict[team] = str(round(team_odds * 100, 3)) + "%"
#
  return json.dumps(odds_dict, indent = 2)


print(simulate())



