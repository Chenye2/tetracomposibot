
from robot import * 

nb_robots = 0
debug = True

class Robot_player(Robot):

    team_name = "avoider"
    robot_id = -1
    iteration = 0

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        translation = sensors[sensor_front]*0.8
        # rotation = 0.5 * (1 - sensors[sensor_front]) + 0.5 * (sensors[sensor_front_left] - sensors[sensor_front_right]) + (random.random()-0.5)*0.15

        rotation = (1 - sensors[sensor_front])*random.choice([1, -1]) - (1 - sensors[sensor_front_left]) + (1 - sensors[sensor_front_right])

        if debug == True:
            if self.iteration % 100 == 0:
                print ("Robot",self.robot_id," (team "+str(self.team_name)+")","at step",self.iteration,":")
                print ("\tsensors (distance, max is 1.0)  =",sensors)
                print ("\ttype (0:empty, 1:wall, 2:robot) =",sensor_view)
                print ("\trobot's name (if relevant)      =",sensor_robot)
                print ("\trobot's team (if relevant)      =",sensor_team)

        self.iteration = self.iteration + 1        
        return translation, rotation, False