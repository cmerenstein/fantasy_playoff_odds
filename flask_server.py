from flask import Flask, jsonify, render_template, request, make_response
import playoff_odds
import pickle

app = Flask(__name__)

def build_game_cell(game, week_num, game_num):
    name1 = playoff_odds.teams[int(game[0])-1]
    name2 = playoff_odds.teams[int(game[1])-1]

    id1 = f"{week_num}-{game_num}-1"
    id2 = f"{week_num}-{game_num}-2"
    cell = f'<div><input type="radio" id="{id1}" data-team="{game[0]}" data-selected="false" onclick=selected(this)>'
    cell += f'<label for="{id1}">{name1}</label>'
    #cell += "<br />vs. <br />"
    cell += "<br />"
    cell += f'<div><input type="radio" id="{id2}" data-team="{game[1]}" data-selected="false" onclick=selected(this)>'
    cell += f'<label for="{id2}">{name2}</label>'
    return cell

def build_schedule_table(schedule):
    t = "<table>"

    for i, week in enumerate(schedule):
        t += f"<tr><th>Week {i+1}</th>"
        for j, game in enumerate(week):
            t += f"<td>{build_game_cell(game, i, j)}</td>"
        t += "</tr>"

    t += "</table>"
    return t

@app.route('/')
def home(methods = ["POST", "GET"]):
  if request.method == "POST":
   data = request.get_json() 
  else:
    fl2 = open("data_2022/schedule.pkl", 'rb') 
    schedule = pickle.load(fl2) 
    print(schedule)
    print(len(schedule))
    return render_template("index.html",
            schedule_table = build_schedule_table(schedule))


@app.route('/post', methods=["POST"])
def get_click():
  picks = {}

  req = request.get_json()
  if "picks" in req:
    for k, v in req["picks"].items():
      picks[int(k)] = v

  ## run simulation
  odds = playoff_odds.simulate(picks=picks)

  print(odds)

  res = make_response(odds, 200)

  return res

if __name__ == "__main__":
  app.run()
