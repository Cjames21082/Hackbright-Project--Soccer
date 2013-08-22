No Sweat Soccer
==========================

No Sweat Soccer is a webapp and management tool for administators in a recreational soccer league.
It has two core functions-
* Create balance teams through player analysis and historical ratings
* Track team and player strength through game performance

The Game:
-------------
This project was built with Python using the Flask framework and Postgresql to store the data. On the front end, I used Bootstrap and some javascript. The core functions were inspired by the the elo rating system from http://en.wikipedia.org/wiki/Elo_rating_system a method for calculating the relative skill levels of players in competitor-versus-competitor games. 

The Teams (create_teams.py)
---------------------------
I used hash mapping to retrieve registered players, sort, and divide them into a variable number of teams.

The team genaration is a automatic feature for the end user. The admin selects the number of desired teams and clicks "Create Magic"
![Create Team](https://raw.github.com/Cjames21082/Hackbright-Project--Soccer/master/app/static/img/create_teams.png)


The Defense (model.py)
------------------------
A team is only as strong as their defense. 

In this project I used the following-

Relational Database- Postgresql 
Currently, there are 12 different tables to manage player and team information.
The User class interacts primarily with the Player_pating, TeamMember, and Game class to pull data needed to update the user's rating. 
The Team class interacts mostly with the Game and SeasonCycle class to monitor teams updates.

ORM- SQLAlchemy with Python

Migration Manager- Alembic 

The Midfield (views.py)
-------------------------
This app is written in Python using the Flask framework. WTF Forms(forms.py) were created to gather user input from the browser.

The app contains a function that modifies a team rating by the following:
* determine the odds (percentage) between competitors using their current rating
* modify rating using the team's current rating, the expected result, the actual result, and a kfactor

The app also modifies a player rating. Additional factors are considered in a player's rating. A player receives a game strength based on their game stats. The player also receives a portion of the win/loss difference from the team ratings. With this data the player's rating is modified based on the elo rating algorithm.

Step 1: Set Match
![Team Rating](https://raw.github.com/Cjames21082/Hackbright-Project--Soccer/master/app/static/img/set_match.png)
Step 2: Record Score
![Team Rating](https://raw.github.com/Cjames21082/Hackbright-Project--Soccer/master/app/static/img/team_rating.png)
Step 3: Update Players
![Team Rating](https://raw.github.com/Cjames21082/Hackbright-Project--Soccer/master/app/static/img/player_rating.png)


Offense (static/templates folders)
-------------------------------------
Flask template pages, Bootstrap, and javascript is used for displaying information.


Overtime- Future Steps
---------------
* Data: 
There are additional factors to analyze a player's strength that I want to investigate
(i.e. likeliness of injury considering age, partime players vs. fulltime players, player's main position, etc.)
* Presentation: 
Improve design and layout for user using javascript and jQuery
              Adding additional features such as email and search option
              Create visual analysis of team and player strength over a time range
* Server: 
Improve processing time (research using a non-relational db for queries)

