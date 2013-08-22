from model import session, User, SeasonCycle, Team, TeamMember

def team_generate(n_teams):


	# list of players
	registered_players = session.query(User).\
						 filter(User.user_registered == True).\
						 all()

	rating ={}

	# create dictionary of registered players by id:rating
	for player in registered_players:
		rating[player.id]= player.getRating()


	# dictionary sorted from lowest to highest
	sorted_rating = sorted(rating.iteritems(), key=lambda (k,v):(v,k))

	#divides the scores into groups lowest to highest
	teams = zip(*[iter(sorted_rating)]* n_teams)
	#print teams
	
	# randomize matrix by reversing every odd row backwards
	count = 1
	shuffled_list =[]
	for row in teams:
		if count%2 == 1:
			shuffled_list.append(row)
			count +=1
		else:
			row = row[::-1]
			shuffled_list.append(row)
			count+=1

	# sum of ratings for each group (testing)
	new_teams = zip(*shuffled_list)

	# for row in new_teams:
	# 	# look at each tuple in row
	# 	each_row = row
	# 	#sum the second element in each tuple in the row
	# 	total = sum([each_row[1] for each_row in row])
	# 	print total

	# Retrieve teams from current cycle
	cycle = session.query(SeasonCycle).order_by(SeasonCycle.id.desc()).first()

	team_name= session.query(Team).\
				filter(Team.seasoncycle == cycle.id).\
				all()

	#Add team_id to players
	team_count = 0 #iterate through rows
	team_id = 0 #place team id in index[0]
	
	player_with_ids =[] # final table
	adjusted_row =[]
	for row in new_teams:
		for tup in row:
			t=list(tup)
			t.insert(team_id, team_name[team_count].id)
			t= tuple(t)
			adjusted_row.append(t)

		team_count +=1
	player_with_ids.append(adjusted_row)

	# #Add players to database
	# for row in player_with_ids:
	# 	for player in row:
	# 		print player
	
	#Add players to database
	for row in player_with_ids:
		for player in row:
			session.add(TeamMember(team_id=player[0],
								   player_id=player[1]))
		session.commit()

# Tests
# team_generate(5)
# team_generate(3)