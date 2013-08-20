from flask import Flask, render_template, redirect, flash, session, url_for, request, g

# connection to LoginHandler in Flask
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required

#connection to forms.py
from forms import LoginForm, RegisterForm, RegisterContForm
from forms import PostForm, TeamForm, SeasonCycleForm, EditProfileForm
from forms import TeamCreateForm, GameForm, ScoreForm, PlayerStatForm

# connection to flask object
from server import app

# connection to model.py
from model import ROLE_ADMIN, ROLE_TEAMLEADER, ROLE_USER
import model
import create_team

from datetime import datetime

#import config pagination
from config import POSTS_PER_PAGE

#import calendar
import calendar, re

from sqlalchemy import and_


#------------End of Imports--------------#

### Start LoginHandler settings

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

@lm.user_loader
def load_user(id):
	return model.session.query(model.User).get(id)

@app.before_request
def before_request():	
	g.user = current_user

	if current_user.is_authenticated():
		# to update the last access time for user 
		# when user has to login again
		current_user.last_seen = datetime.utcnow()
		model.session.add(current_user)
		model.session.commit()
### End LoginHandler settings


@app.route('/')
def homepage():
	# determine if registration is open
	open_registration = model.registration()

	season = model.current_season()
	
	if not season:
		season = None
	
	return render_template('index.html',
							title='Homepage',
							open_registration= open_registration,
							season= season)


@app.route('/calendar', methods=["GET", "POST"])
@login_required
def get_calendar():
	form = GameForm()

	today = request.args.get('month')

	if today == None:
		today = datetime.date(datetime.now())

	print today
	# --------calendar begins---------#
	year = ['January', 
			 'February', 
			 'March', 
			 'April', 
			 'May', 
			 'June', 
			 'July', 
			 'August', 
			 'September', 
			 'October', 
			 'November', 
			 'December'] 

	# by default the calendar begin the week with Monday (day 0)
	
	calendar.setfirstweekday(calendar.SUNDAY)
	
	#stiringify date and reorganize into integers
	current = re.split('-', str(today))

	current_no = int(current[1])
	current_month = year[current_no - 1]
	current_day = int(re.sub('\A0', '',current[2]))
	current_yr = int(current[0])


	month = calendar.monthcalendar(current_yr, current_no) 
	nweeks = len(month) 

	each_week=[]
	
	for w in range(0,nweeks): 
		week = month[w]
		each_week.append(week)
	#---------------calender ends-----------#

	#-----add matches--------#
	all_teams = model.current_teams()

	teams={}	    
	for t in all_teams:
		teams[t.id]=t.teamname

	# render template to set games
	form= GameForm()

	games = model.session.query(model.Game).\
			order_by(model.Game.game_date.desc()).all()

	if form.validate_on_submit():
		if form.home_team.data == form.away_team.data:
			flash("Teams cannot be the same")
			return redirect('calendar')
		else:
			new_game= model.session.\
					  add(model.Game(game_date = form.game_date.data,
								home_team = form.home_team.data,
								away_team = form.away_team.data,
								home_score = form.home_score.data,
								away_score = form.away_score.data))

			model.session.commit()
			flash('Game Added!')
			return redirect('calendar')	

	#----------render form to change score---#
	form_s = ScoreForm()

	return render_template('calendar.html',
						    title='Calendar',
						    current_month= current_month,
						    current_yr= current_yr,
						    each_week = each_week,
						    user= current_user,
						    form=form,
						    games=games,
						    form_s=form_s,
							all_teams=all_teams,
							teams=teams
						    )

@app.route('/schedule', methods=["GET","POST"])
@login_required
def show_matches():

	all_teams = model.current_teams()

	teams={}	    
	for t in all_teams:
		teams[t.id]=t.teamname

	games = model.session.query(model.Game).\
			order_by(model.Game.game_date.desc()).all()

	#----------render form to change score---#
	form_s = ScoreForm()

	return render_template('schedule.html',
						    title='Matches',
						    games=games,
						    form_s=form_s,
							all_teams=all_teams,
							teams=teams
						    )


@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
	form = EditProfileForm()

	if form.validate_on_submit():
		current_user.firstname = form.firstname.data
		current_user.lastname = form.lastname.data
		current_user.address = form.address.data
		current_user.city = form.city.data
		current_user.state = form.state.data
		current_user.zipcode = form.zipcode.data
		current_user.country = form.country.data
		current_user.about_me = form.about_me.data
		current_user.user_disabled = form.user_disabled.data

		model.session.add(current_user)
		model.session.commit()

		flash('Your changes have been saved!')
		return redirect(url_for('edit'))
		#renders the fields with data from database
	else:
		form.firstname.data= current_user.firstname
		form.lastname.data= current_user.lastname 
		form.address.data= current_user.address 
		form.city.data= current_user.city 
		form.state.data= current_user.state
		form.zipcode.data= current_user.zipcode
		form.country.data= current_user.country
		form.about_me.data= current_user.about_me
		form.user_disabled.data= current_user.user_disabled

	return render_template("edit_profile.html",
							form=form)



@app.route('/game_delete', methods=["POST"])
@login_required
def game_delete():
	
	delete_game = request.form['delete_game']


	model.session.query(model.Game).\
	filter(model.Game.id == int(delete_game)).\
	delete()

	model.session.commit()

	return redirect('schedule')


@app.route('/game_edit', methods=["GET", "POST"])
@login_required
def game_edit():
	#---------Edit score for matches---------#
	form_s = ScoreForm()

	game_id= request.form['edit_game']
	game= model.session.query(model.Game).get(int(game_id))

	if form_s.validate_on_submit():
		form_s.game_date = game.game_date
		form_s.home_team = game.home_team
		form_s.away_team = game.home_team
		game.home_score = form_s.home_score.data
		game.away_score = form_s.away_score.data

		model.session.add(game)
		model.session.commit()

		flash('Your changes have been updated. Select \'Save\' to finalize!')
		return redirect('schedule')


@app.route('/game_stats', methods=['GET', 'POST'])
@login_required
def player_stats():	

	form = PlayerStatForm()

	game_id = request.args.get('game')
	
	if game_id == None:
		game_id = request.form['game']

	game = model.session.query(model.Game).get(game_id)
	
	player_stats = model.session.query(model.PlayerStat).\
				   filter(model.PlayerStat.game_id == game_id).\
				   all()
	
	#get team players
	home_team = model.session.query(model.Team).get(game.home_team)
	away_team = model.session.query(model.Team).get(game.away_team)
	home_players = home_team.members
	away_players = away_team.members
	
	if request.method == 'GET':

		return render_template('player_update.html',
							title='RecordPlayer',
							form=form,
							home_players = home_players,
							away_players= away_players,
							game = game,
							player_stats= player_stats)

	if request.method == 'POST':
	#enter player data
		if form.validate_on_submit():
			game_id = request.form['game']
			
			player_name = request.form['name']
			player = model.session.query(model.User).\
					 get(player_name)
			player_id = player.id
			print player_id

			dup_entry = model.session.query(model.PlayerStat).\
						join(model.Game, model.Game.id == model.PlayerStat.game_id).\
						filter(and_(model.Game.id == game_id,
					    model.PlayerStat.player_id == player.id)).first()
			
			#check for duplicate entry

			if dup_entry != None:
				flash('Player entry already made. Delete and Re-Enter')
				return redirect("game_stats?game=" + str(game_id))
			else:
				new_stat = model.session.add(model.PlayerStat(game_id= game_id,
											 player_id= player_id,
											 goals=form.goals.data,
											 assists= form.assists.data,
											 absence= form.absence.data,
											 goalie_loss= form.goalie_loss.data,
											 goalie_win= form.goalie_win.data))
			
				model.session.commit()
				

				last_entry = model.session.query(model.PlayerStat).\
							 order_by(model.PlayerStat.id.desc()).first()

				model.PlayerStat.calculate_stat(last_entry)
				model.session.commit()
				flash("Player Status Updated")

				# refresh list of stats
				player_stats = model.session.query(model.PlayerStat).\
					   filter(model.PlayerStat.game_id == game_id).\
					   all()
				
				return redirect("game_stats?game=" + str(game_id))
						

@app.route('/game_record', methods=["GET", "POST"])
@login_required
def update_teamRating():

	game_id= request.form['record_game']
	game= model.session.query(model.Game).get(int(game_id))

	game.game_saved =True
	model.session.add(game)
	# Add win/loss/tie 
	model.Game.calculate_score(game)
	# commit all changes
	model.session.commit()
	
	# Home calculations
	home_id = game.home_team
	home_rating = model.session.query(model.Team).\
					  get(home_id).getRating()
	
	home_result= game.home_win + game.home_tie + game.home_loss
	# Away calculations
	away_id = game.away_team
	away_rating = model.session.query(model.Team).\
					  get(away_id).getRating()
	
	away_result= game.away_win + game.away_tie + game.away_loss
	#Update team rating
	expectation = model.getExpectation(home_rating, away_rating)
	new_home_rating = model.modifyTeamRating(home_rating, expectation,home_result, 32)
	new_away_rating = model.modifyTeamRating(away_rating, expectation,away_result, 32)
	# Add new rating
	model.session.add(model.TeamRating(team_id=game.home_team,
									   game_id=game.id,
									   team_rating= new_home_rating))

	model.session.add(model.TeamRating(team_id=game.away_team,
									   game_id=game.id,
									   team_rating= new_away_rating))
	model.session.commit()

	# Update game record to calculate player ratings

	home_diff = new_home_rating - home_rating
	away_diff = new_away_rating - away_rating
	game.expectation = expectation
	game.home_differential = home_diff
	game.away_differential = away_diff
	model.session.add(game)
	model.session.commit()


	flash('Your changes have been saved!')
	return redirect('schedule')


@app.route('/login', methods=['GET','POST'])
def login():
	# determine if registration is open; checks flag
	open_registration = model.registration()

	# if user hasn't logged out redirect don't reload login page
	if current_user is not None and current_user.is_authenticated():
		return redirect(url_for('user'))

	form = LoginForm()
	if form.validate_on_submit():

		user= model.session.query(model.User).\
			  filter_by(email=form.email.data, password=form.password.data).\
			  first()
	
		if user is not None:
			login_user(user)	
			flash("Welcome")
		else:
			flash("Invalid login")

		#pass arg to user profile
		
		return redirect(request.args.get("next") or url_for('user'))
		
	
	return render_template('login.html',
							title='Sign In',
							form=form,
							open_registration= open_registration)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect('/')



@app.route('/player_update', methods=['POST'])
@login_required
def update_playerRating():
	game_id= request.form["game"]
	stat_id= request.form["stats"]
	player_id = request.form["player"]
	
	# retrieve player, team, game, and stat record
	player_stat = model.session.query(model.PlayerStat).get(stat_id)

	game= model.session.query(model.Game).get(game_id)

	player= model.session.query(model.User).get(player_id)

	team_id= model.session.query(model.TeamMember).\
		  join(model.Team, model.Team.id == model.TeamMember.team_id).\
		  join(model.User, model.User.id == model.TeamMember.player_id).\
		  filter(model.User.id == player_id).\
		  first()

	team = model.session.query(model.Team).get(team_id.team_id)

	#update player rating
	diff = None
	game_result = None
	if game.home_team == team.id:
		diff = game.home_differential
		game_result = game.home_win + game.home_loss + game.home_tie
	else:
		diff = game.away_differential
		game_result = game.away_win + game.away_loss + game.away_tie

	
	team_points = (float(player.getRating())/float(team.getRating())) * diff
	current_rating = player.getRating()
	kfactor = 32
	strength = player_stat.strength
	expectation = game.expectation

	update_rating = model.modifyPlayerRating(current_rating, expectation, 
											 game_result,strength, team_points, 
											 kfactor)
	print player_stat.absence

	if player_stat.absence != True:
		model.session.add(model.PlayerRating(team_id=team.id,
											 game_id=game_id,
											 player_id= player_id,
											 player_rating= update_rating))

	# change stat record to save; user can no longer edit
	player_stat.stat_saved = True
	model.session.add(player_stat)

	model.session.commit()

	return redirect("game_stats?game=" + str(game_id))



@app.route('/post_edit', methods=['POST'])
@login_required
def post_edit():
	
	post= request.form['edit_post']

	#print post

	model.session.query(model.Post).\
	filter(model.Post.id == int(post)).\
	delete()

	model.session.commit()

	return redirect(url_for('user'))



@app.route('/register', methods=['GET','POST'])
def register():
	form = RegisterForm()

	if form.validate_on_submit():
	# check if email already exists
		email_exists = model.session.query(model.User).\
		               filter_by(email = form.email.data).first()
	
		if email_exists != None:
			flash('Email already exists')
			return render_template('register.html', 
				                    title='Register', 
				                    form=form)
		else:
			user = model.session.\
				   add(model.User(firstname= form.firstname.data,
								  lastname= form.lastname.data,
								  email= form.email.data,
								  password= form.password.data,
								  address= form.address.data,
								  city= form.city.data,
								  state= form.state.data,
								  zipcode= form.zipcode.data,
								  country= form.country.data,
								  dob= form.dob.data,
								  gender= form.gender.data))
		    # add user
			model.session.commit()

			flash("Registration almost done. Login to complete.")
		   	#user must login with new email/password
			return redirect(url_for('login'))

	return render_template('register.html',
							title='Register',
							form=form)

@app.route('/register_cont', methods=['GET', 'POST']) # To fix, delete not working properly
@login_required
def register_cont():
	form= RegisterContForm()

	if form.validate_on_submit():

		current_user.fitness = int(form.fitness.data)
		current_user.experience = int(form.experience.data)
		current_user.willing_teamLeader = form.willing_teamLeader.data

		# Add positions
		if current_user.positions != []:
			for position in current_user.positions:
				model.session.delete(position)

		for value in form.positions.data:
			model.session.add(model.Position(user_id=current_user.id, position_type=value))


		# Add health_issues
		if current_user.health_issues != []:
			for issue in current_user.health_issues:
				model.session.delete(issue)

		for value in form.health.data:
			model.session.add(model.UserHealth(user_id=current_user.id, health_id=int(value)))

		current_user.user_registered = True

		model.session.commit()

		#add update to rating
		current_user.getRating()
		
		flash("Registration Complete")
		#user directed to profile page
		return redirect(url_for('user'))
				
	return render_template('register_cont.html', 
							title="RegisterCont", 
							form=form)

@app.route('/seasons', methods=['GET'])
@login_required
def seasons():

	return render_template('season.html',
							title='Season')


@app.route('/seasons_create', methods=['GET', 'POST'])
@login_required
def create_season():
	#load users to reset when new cycle created
	users= model.session.query(model.User).all()

	# load form to create new season_cycle (form)
	form = SeasonCycleForm()

	# create new cycle

	if form.validate_on_submit():
		cycle = model.session.\
				add(model.SeasonCycle(admin_id= current_user.id,
									  leaguename= form.leaguename.data,
									  cyclename= form.cyclename.data,
									  num_of_teams= form.num_of_teams.data,
									  home_region= form.home_region.data,
									  fee_resident= form.fee_resident.data,
									  fee_nonresident= form.fee_nonresident.data,
									  reg_start= form.reg_start.data,
									  reg_end= form.reg_end.data,
									  active= True))	
		#print form.errors		
		model.session.commit()

		# reset all users to false
		for user in users:
			user.user_registered = False

		model.session.commit()
		flash("Cycle created")
		return redirect('seasons')

	
	return render_template('season_create.html',
						title='SeasonCreate',
						form=form)


@app.route('/seasons_edit', methods=['GET','POST'])
@login_required
def edit_season():	
	current_cycle = model.session.query(model.SeasonCycle).\
					filter(model.SeasonCycle.active ==True).\
					first()

	message = ""

	form = SeasonCycleForm()

	# if registration for the last season is closed
	if current_cycle == None:
		message = "Registration is closed. You can no longer edit."
	   
	   	current_cycle = model.session.query(model.SeasonCycle).\
					   	order_by(model.SeasonCycle.id.desc()).\
					   	first()
	
    #Check which submit button is clicked
	if request.form.get("current_season") == 'edit' and form.validate_on_submit() :
		# edit current season if status is active
		current_cycle.leaguename= form.leaguename.data 
		current_cycle.cyclename= form.cyclename.data 
		current_cycle.num_of_teams= form.num_of_teams.data 
		current_cycle.home_region= form.home_region.data 
		current_cycle.fee_resident= form.fee_resident.data
		current_cycle.fee_nonresident= form.fee_nonresident.data
		current_cycle.reg_start= form.reg_start.data
		current_cycle.reg_end= form.reg_end.data 

		model.session.add(current_cycle)
		model.session.commit()
		

		flash('Your changes have been saved!')
		
	else:
		#renders the fields with data from database
		form.leaguename.data= current_cycle.leaguename 
		form.cyclename.data= current_cycle.cyclename
		form.num_of_teams.data= current_cycle.num_of_teams 
		form.home_region.data= current_cycle.home_region
		form.fee_resident.data= current_cycle.fee_resident
		form.fee_nonresident.data= current_cycle.fee_nonresident
		form.reg_start.data= current_cycle.reg_start
		form.reg_end.data= current_cycle.reg_end 
	
		
	if request.form.get("current_season") == 'close':

		
		current_cycle.active = False
		model.session.commit()	
		
		return redirect('seasons_edit')
	

	return render_template("season_edit.html",
						title= 'SeasonEdit',
						form=form,
						current_cycle= current_cycle,
						message=message)


@app.route('/seasons_view', methods=['GET'])
@login_required
def review_season():
	
	# generate list for Past Cycle Dropdown
	all_cycles = model.session.query(model.SeasonCycle).\
				 order_by(model.SeasonCycle.id.desc()).all()
	past_cycle = None
	# load form to create new season_cycle (form)
	form = SeasonCycleForm()
	

	# From user input retrieve selected cycle
	cycle_id = request.args.get("cycle_history")
	
	if cycle_id != None:
		past_cycle = model.session.query(model.SeasonCycle).\
					 get(int(cycle_id))

		form.leaguename.data = past_cycle.leaguename
		form.cyclename.data = past_cycle.cyclename
		form.num_of_teams.data = past_cycle.num_of_teams
		form.home_region.data = past_cycle.home_region
		form.fee_resident.data= past_cycle.fee_resident
		form.fee_nonresident.data= past_cycle.fee_nonresident
		form.reg_start.data= past_cycle.reg_start
		form.reg_end.data = past_cycle.reg_end

	return render_template('season_view.html',
						title='SeasonView',
						form=form,
						all_cycles= all_cycles,
						past_cycle= past_cycle)


@app.route('/stat_delete', methods=['POST'])
@login_required
def delete_stat():

	game_id = request.form["game"]
	stat_id = request.form["delete_stat"]
	
	player_stat = model.session.query(model.PlayerStat).get(stat_id)
	
	model.session.delete(player_stat)
	model.session.commit()

	return redirect("game_stats?game=" + str(game_id))


@app.route('/teams', methods=['GET'])
@login_required
def teams():

	return render_template('teams.html',
							title='Teams')


@app.route('/team_create', methods=['GET','POST'])
@login_required
def create_teams():

	current_season = model.current_season()
	teams = model.session.query(model.Team).\
				join(model.SeasonCycle, model.Team.seasoncycle == current_season.id).\
				all()


	form= TeamCreateForm()


	team_members = model.session.query(model.TeamMember).\
				   join(model.Team, model.Team.id == model.TeamMember.team_id).\
				   join(model.SeasonCycle, model.Team.seasoncycle == current_season.id)
	

	if form.validate_on_submit():
		if team_members != None:
			for member in team_members:
				model.session.delete(member)

			model.session.commit()

		create_team.team_generate(int(form.team_num.data))

	
	return render_template('teams_create.html',
							title='TeamCreate',
							team_members=team_members,
							form=form, 
							current_season=current_season,
							teams=teams)


@app.route('/team_names', methods=['GET', 'POST'])
@login_required
def teamname():
	#Determinant for current season
	max_teams = 0
	teams = None
	team_count = 0
	
	current_season = model.session.query(model.SeasonCycle).\
		             order_by(model.SeasonCycle.id.desc()).first()
    
	print current_season.id 

	if current_season is not None:
		# created teams by cycle.id
		teams = model.session.query(model.Team).\
				filter(model.Team.seasoncycle == current_season.id).\
				all()

		team_count= len(teams)

		# number of teams based on season cycle
		max_teams = current_season.num_of_teams

	#Create Team Names
	form = TeamForm()

	if form.validate_on_submit():
	
		new_team = model.session.\
				   add(model.Team(teamname= form.teamname.data,
				   				  seasoncycle= current_season.id))

		model.session.commit()
		return redirect('team_names')

	return render_template('team_names.html',
							title='Teamname',
							form=form,
							max_teams=max_teams,
							teams= teams,
							team_count= team_count,
							current_season=current_season)



@app.route('/team_leaders', methods=['GET','POST'])
@login_required
def role_assignment():
	form= TeamCreateForm()

	#Get team_id
	team_list = request.args.get("list")
	if team_list != None:
		team_list = int(team_list)
	else:
		team_list = None
	
	# loan users to determine captain, admin, and teammembers
	team_members = model.session.query(model.TeamMember).all()

	users= model.session.query(model.User).\
		   filter(model.User.user_registered == True)

	admins= users.filter(model.User.role == ROLE_ADMIN).all()
	captains = users.filter(model.User.role == ROLE_TEAMLEADER).all()
	

	count_players = model.session.query(model.User).count()
	count_captains = len(captains)
	count_admins = len(admins)

	if request.method == 'POST':
		try:
			captain = request.form["captain"]
			player = model.session.query(model.User).get(int(captain))
			player.update_role(ROLE_TEAMLEADER)
			print player.role
		except KeyError:
			pass

		try:
			admin= request.form["admin"]
			player = model.session.query(model.User).get(int(admin))
			player.update_role(ROLE_ADMIN)	
			print player.role
		except KeyError:
			pass

		try:
			undo= request.form["undo"]
			player = model.session.query(model.User).get(int(undo))
			player.undo_role()
			print player.role
		except KeyError:
			pass

		model.session.commit()

		# refresh list
		admins= users.filter(model.User.role == ROLE_ADMIN).all()
		captains = users.filter(model.User.role == ROLE_TEAMLEADER).all()
		count_captains = len(captains)
		count_admins = len(admins)
	
	return render_template("team_leaders.html", 
							users= users,
							admins= admins,
							captains= captains,
							count_players=count_players,
							count_captains= count_captains,
							count_admins= count_admins,
							form=form,
							team_list=team_list,
							team_members= team_members)


@app.route('/team_save', methods=['GET','POST'])
@login_required
def save_teams():
	# change flag for season to saved= True
	current_season = model.current_season()
	current_season.saved =True
	model.session.add(current_season)

	#add intital team ratings
	for team in model.current_teams():
		team.getRating()

	model.session.commit()

	# This will disable team name and creation button

	return redirect('team_create')




@app.route('/user', methods=['GET','POST'])
@login_required
def user():	

	user_id = request.args.get("user_id")

	if user_id == None:
		user_id = current_user.id

	# enable registration link
	current_cycle = model.session.query(model.SeasonCycle).\
					order_by(model.SeasonCycle.id.desc()).\
					first()
	
	#print current_cycle.cyclename
	
	users= model.session.query(model.User)
	user = users.get(user_id)
	
	form= PostForm()

	if form.validate_on_submit():
		new_post = model.session.\
				   add(model.Post(body=form.post.data,
				   				  user_id= g.user.id))

		model.session.commit()
		flash('Your post is live!')
		return redirect('user')

	return render_template('user.html',
							title= 'Profile',
							users=users,
							user = user,
							current_cycle=current_cycle,
							form=form)


@app.route('/view_players', methods=['GET'])
@login_required
def view_players():
	
	#Start with all users
	users = model.session.query(model.User)
	

	# All healthtypes for dropdwon menu healthtypes
	health_issues = model.session.query(model.HealthType).\
					order_by(model.HealthType.id).all()

	#get filter variables
	position = request.args.get("position")
	print position
	fitness = request.args.get("fitness")
	print fitness
	health = request.args.get("health")
	print health

	### Begin Filter
	if position != "all" and position != None:
		users = users.join(model.Position, model.User.id == model.Position.user_id).\
				filter(model.Position.position_type == position)
	
	if fitness != "0" and position != None:
		users = users.filter(model.User.fitness == int(fitness))

	if health != "0" and position != None:
		users = users.join(model.UserHealth, model.User.id == model.UserHealth.user_id).\
				filter(model.UserHealth.health_id == int(health))
	
	return render_template('view_players.html', 
							title='View Players',
							users=users,
							health_issues=health_issues)