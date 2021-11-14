from flask import Flask, jsonify, render_template, request, make_response
import playoff_odds

app = Flask(__name__)

@app.route('/')
def home(methods = ["POST", "GET"]):
  if request.method == "POST":
   data = request.get_json() 
  else:
    return render_template("index.html") 


@app.route('/post', methods=["POST"])
def get_click():
  req = request.get_json()
  print(req)

  ## run simulation
  odds = playoff_odds.simulate()

  res = make_response(odds, 200)

  return res

if __name__ == "__main__":
  app.run()
