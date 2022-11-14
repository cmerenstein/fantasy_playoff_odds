
var b1 = document.getElementById("b1")
var buttons = document.getElementsByClassName("button")

document.onload = reset_table

console.log(buttons)

b1.onclick = read_table

function submit(picks)  {

  fetch('/post', {
    method: "POST",
    credentials: "include",
    body: JSON.stringify({"picks":picks}),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })
    .then(function (response) {
        if (response.status !== 200) {
          console.log(`Looks like there was a problem. Status code: ${response.status}`);
          return;
     }
        response.json().then(function (data) {
          console.log(data);

          var odds = document.getElementsByClassName("odds")
          console.log(odds)
          
          for (team in data){
            console.log(team)
            console.log(odds[team])
            console.log(data[team])
            
            odds[team].innerHTML = data[team]
          }

        });
      })
      .catch(function (error) {
        console.log("Fetch error: " + error);
   }); 

}

function selected(t) {
	console.log(t);
	console.log(t.dataset.selected);
	if (t.dataset.selected == "false") {
		t.dataset.selected = "true";
		console.log("uh");
	} else {
		t.dataset.selected = "false";
		t.checked = false;
	}

	// Make sure only one is selected
	if (t.checked) {
		base_id = t.id.substr(0, t.id.length-1);
		team_num = t.id.substr(-1);
		if (team_num == "1") {
			document.getElementById(base_id+"2").checked = false;
		} else {
			document.getElementById(base_id+"1").checked = false;
		}
	}

	read_table();
}

function read_table() {
  res = {};
  for (let week = 0; week < 15; week++) {
    week_res = [];
    for (let game = 0; game < 4; game++) {
      team1 = document.getElementById(week+"-"+game+"-1");
      team2 = document.getElementById(week+"-"+game+"-2");
      if (team1.checked) {
        week_res.push(team1.dataset.team)

        if (team2.checked) {
          console.log("!!! both teams selected");
        }
      } else if (team2.checked) {
        week_res.push(team2.dataset.team)
      }
    }
    res[week] = week_res;
  }
  console.log(res);

  submit(res);
}

function reset_table() {
  for (let week = 0; week < 15; week++) {
    week_res = [];
    for (let game = 0; game < 4; game++) {
      document.getElementById(week+"-"+game+"-1").checked = false;
      document.getElementById(week+"-"+game+"-2").checked = false;
    }
  }
}
