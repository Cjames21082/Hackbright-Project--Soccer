import math

class elo_core:
  def getExpectation(rating_1, rating_2):
    calc = (1.0 / (1.0 + pow(10, ((rating_2 - rating_1) / 400))));
    return calc
 
  def modifyTeamRating(rating, expected, actual, kfactor):
  	return modifyRating(rating, expected, actual, kfactor)

  def modifyPlayerRating(rating, expected, actual, kfactor):
  	return modifyRating(rating, expected, actual, kfactor)

  def modifyRating(rating, expected, actual, kfactor):
    calc = (rating + kfactor * (actual - expected))
    return calc

  # modify last rating with strength qualities at the beginning of each season
  def modifyRating_Strength(rating, dob, fitness, experience, health):
    calc= rating + dob + fitness + experience + health
    return calc