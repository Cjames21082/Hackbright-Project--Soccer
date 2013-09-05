from model import session, User, SeasonCycle, Team, TeamMember
import model

def team_generate(n_teams):
	#list of players
	registered_players = session.query(User).\
							 filter(User.user_registered == True).\
							 all()

	# list sorted lowest to highest
	sorted_rating = sorted(registered_players, key=lambda i: i.getRating())

	# create a matrix of n_teams with spaces for all registered players
	# list comprehension for parameters is better than multiplication
	# the plus 1 adds an additional space if registered players not evenly divisible by n_teams
	teams = [[None for l in range(len(sorted_rating)/n_teams+1)] for n in range(n_teams)]

	count=0
	team_spot= 0
	
	while sorted_rating:
		teams[count][team_spot] = sorted_rating.pop(0)
		count +=1

		if count == n_teams:
			# sort team rows from highest to lowest since I'm placing players on from lowest to highest
			teams[::-1] = sorted(teams, key=lambda x: [[sum([row.getRating() for row in team[:team_spot]])]for team in teams])
		
			#reset counters
		  	count= 0
		  	team_spot += 1
	
	current_cycle = model.current_season()

	team_names= session.query(Team).\
		   		join(SeasonCycle, Team.seasoncycle == current_cycle.id).\
		   		all()
	print team_names[0].id

	#Add players to teams in database
	count =0
	for team in teams:
		for player in team:
			if player != None:
				session.add(TeamMember(team_id=team_names[count].id,
								   	    player_id=player.id))
				session.commit()

		count +=1

# Tests
team_generate(5)
# team_generate(3)