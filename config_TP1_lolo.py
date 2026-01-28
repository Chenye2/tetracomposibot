# Configuration file.

import arenas

# general -- first three parameters can be overwritten with command-line arguments (cf. "python tetracomposibot.py --help")

display_mode = 0
arena = 0
position = False 
max_iterations = 501 #401*500

# affichage

display_welcome_message = False
verbose_minimal_progress = True # display iterations
display_robot_stats = False
display_team_stats = False
display_tournament_results = False
display_time_stats = True

# initialization : create and place robots at initial positions (returns a list containing the robots)

import robot_dumb
import robot_wanderer

import robot_braitenberg_loveBot
import robot_braitenberg_hateBot

def initialize_robots(arena_size=-1, particle_box=-1): # particle_box: size of the robot enclosed in a square
    x_center = arena_size // 2 - particle_box / 2
    y_center = arena_size // 2 - particle_box / 2
    robots = []

    robots.append(robot_dumb.Robot_player(x_center, y_center, 0, name="My Robot", team="A"))
    #robots.append(robot_wanderer.Robot_player(x_center, y_center, 0, name="My Robot", team="A"))

    robots.append(robot_braitenberg_loveBot.Robot_player(x_center - 3, y_center, 0, name="My Robot", team="B"))

    #robots.append(robot_braitenberg_hateBot.Robot_player(x_center - 3, y_center - 2, 0, name="My Robot", team="B"))
    
    return robots