import math
import random
from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "SIXSEVEN"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    # statégie optimisée simulée
    bestParam = [1, 1, -1, 1, -1, 1, 1, -1] # score 869
    # bestParam = [1, 0, 1, 1, -1, 1, 1, -1] # score 976

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        front = sensors[sensor_front]
        left = sensors[sensor_front_left]
        right = sensors[sensor_front_right]

        sensor_to_wall = []
        sensor_to_robot = []
        for i in range (0,8):
            if  sensor_view[i] == 1:
                sensor_to_wall.append( sensors[i] )
                sensor_to_robot.append(1.0)
            elif  sensor_view[i] == 2:
                sensor_to_wall.append( 1.0 )
                sensor_to_robot.append( sensors[i] )
            else:
                sensor_to_wall.append(1.0)
                sensor_to_robot.append(1.0)

        # robot 0 : prendre maximum de cases (braitenberg avoider)
        if self.robot_id == 0 or self.robot_id == 2 :
            # niveau 1 
            if front < 0.5 or left < 0.4 or right < 0.4:
                self.memory = -15
            if self.memory < 0:
                self.memory += 1
                translation = 0.05
                # tourner pour sortir du coin
                if abs(left - right) < 0.05:
                    rotation = random.choice([-1, 1])
                else:
                    rotation = -1 if left < right else 1
                
            
            # niveau 2 : comportement Braitenberg avoider
            if front < 0.8 or left < 0.8 or right < 0.8:
                self.memory = 0
                translation = front
                rotation = 0.5 * (1 - sensors[sensor_front]) + 0.5 * (sensors[sensor_front_left] - sensors[sensor_front_right]) + (random.random()-0.5)*0.15

            # niveau 3 : exploration
            else:
                self.memory = 0
                translation = 0.7
                rotation = (random.random() - 0.5) * 0.3

        # robot 1 : robot stalker (braitenberg loveBot)
        if self.robot_id == 1 or self.robot_id == 3:
             # mode d'échappement : si mur ou robot très proche
            if (front < 0.4 or left < 0.3 or right < 0.3):
                self.memory = -15 # mode d'échappement pendant 15 itérations
            if self.memory < 0:
                self.memory += 1
                translation = 0.05
                # tourner pour sortir du coin
                if abs(left - right) < 0.05:
                    rotation = random.choice([-1, 1])
                else:
                    rotation = -1 if left < right else 1
            
            # niveau 1 : si robot adverse détecté devant, se diriger vers lui
            elif ((sensor_to_robot[sensor_front] < 0.8 and sensor_team[sensor_front] != self.team_name) or
                  (sensor_to_robot[sensor_front_left] < 0.8 and sensor_team[sensor_front_left] != self.team_name) or
                  (sensor_to_robot[sensor_front_right] < 0.8 and sensor_team[sensor_front_right] != self.team_name)):

                self.memory = 0
                
                translation = sensors[sensor_front]*0.3 + 0.5
                rotation = 0.8 * (sensor_to_robot[sensor_front_right] - sensor_to_robot[sensor_front_left]) + 0.5 * (sensor_to_robot[sensor_right] - sensor_to_robot[sensor_left])
            
            # niveau 2 : si mur ou robot même équipe détecté devant, l'éviter 
            elif front < 0.8 or left < 0.6 or right < 0.6:
                self.memory = 0
                translation = front
                rotation = 0.5 * (1 - sensors[sensor_front]) + 0.8 * (sensors[sensor_front_left] - sensors[sensor_front_right]) + (random.random()-0.5)*0.15

            # niveau 3 : exploration si pas de robot adverse détecté
            else:
                self.memory = 0
                translation = 0.8
                rotation = (random.random() - 0.5) * 0.3

        return translation, rotation, False
