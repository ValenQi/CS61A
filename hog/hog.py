# CS 61A Spring 2015 
# Names: Yaxin Yu(Login: cs61a-alp)
#        Qi Liu(Login: cs61a-anf)

"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times. Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    i, sum_of_outcome, pig_out = 1, 0, False
    while i <= num_rolls:
        current_outcome = dice()
        sum_of_outcome, i = sum_of_outcome + current_outcome, i + 1
        if current_outcome == 1:
            pig_out = True
    if pig_out:
        return 1
    return sum_of_outcome

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    if num_rolls == 0:
        tens, ones = opponent_score//10, (opponent_score % 10)
        return 1 + max(tens, ones)
    else:
        return roll_dice(num_rolls, dice)
    

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """
    if (score + opponent_score) % 7 == 0:
        return four_sided
    return six_sided

def is_prime(n):
    """Return True if a non-negative number N is prime, otherwise return
    False. 1 is not a prime number!
    """
    assert type(n) == int, 'n must be an integer.'
    assert n >= 0, 'n must be non-negative.'
    if n <= 1:
        return False
    k = 2
    while k < n:
        if n % k == 0:
            return False
        k += 1
    return True


def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, score0=0, score1=0, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first
    strategy1:  The strategy function for Player 1, who plays second
    score0   :  The starting score for Player 0
    score1   :  The starting score for Player 1
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    while score0 < goal and score1 < goal:  
        dice = select_dice(score0, score1)
        num_of_roll = strategy1(score1, score0) if who else strategy0(score0, score1)
        current_turn_score = take_turn(num_of_roll, score0 if who else score1, dice)
        if who:
            score1 += current_turn_score
        else:
            score0 += current_turn_score
        if is_prime(score0 + score1) and score0 != score1:
            if score0 > score1:
                score0 += current_turn_score
            else:
                score1 += current_turn_score
        who = other(who)
    return score0, score1  



#######################
# Phase 2: Strategies #
#######################

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def fn_averaged(*args):
        i, sum = 1, 0
        while i <= num_samples:
            sum += fn(*args)
            i += 1
        return sum / num_samples
    return fn_averaged


def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Assume that dice always
    return positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    i, array_of_roll_num = 1, []
    while i <= 10:
        current_average = make_averaged(roll_dice)(i, dice)
        array_of_roll_num.append(current_average)
        i += 1
    return array_of_roll_num.index(max(array_of_roll_num)) + 1

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test prime_strategy
        print('prime_strategy win rate:', average_win_rate(prime_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    if take_turn(0,opponent_score) >= margin:
        return 0
    return num_rolls

def prime_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it results in a beneficial boost and
    rolls NUM_ROLLS if rolling 0 dice gives the opponent a boost. It also
    rolls 0 dice if that gives at least MARGIN points and rolls NUM_ROLLS
    otherwise.
    """
    score += take_turn(0,opponent_score)   
    if is_prime(score + opponent_score) and score != opponent_score:
        if score > opponent_score:
            return 0
        return num_rolls
    if take_turn(0,opponent_score) >= margin:
        return 0
    return num_rolls

def general_strategy(score, opponent_score):
    """Given scores before a turn, return 4 if roll a 4_sided die,
    and 6 if roll a 6_sided die in order to maximize outcome"""
    if (score + opponent_score) % 7 == 0:
        return 4
    return 6

def final_strategy(score, opponent_score):
    """Final strategy returns different roll numbers in 4 different cases.
    Case 1: roll 0 (free bacon) if it will either give opponent a 4-sided die 
            or boost my score (hogtimus prime).
    Case 2: take risk if I am falling behind:
            roll 1 extra time for every 10-point difference.
    Case 3: if score is approaching 100(>= 70), roll 0 to avoid Pig_Out.
    Case 4: if none of the above cases apply, apply General_Strategy 
            (roll four 4_sided dice or six 6_sided dice).
    """
    #Case 1:  
    score_after_bacon = score + max(opponent_score//10, opponent_score % 10) + 1    
    hogtimus_prime = is_prime(score_after_bacon + opponent_score) and (score_after_bacon > opponent_score)                   
    if (score_after_bacon + opponent_score) % 7 == 0 or hogtimus_prime:
        return 0
    #Case 2: 
    if opponent_score - score >= 10:
        num_rolls = general_strategy(score, opponent_score) + (opponent_score - score) // 10
        return min(num_rolls, 10)             # cannot roll more than 10 times
    #Case 3: 
    if score >= 70:
        return 0
    #Case 4:     
    return general_strategy(score, opponent_score)

##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()