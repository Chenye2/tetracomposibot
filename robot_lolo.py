import math
import random
from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "SÉPADELIA"  # vous pouvez modifier le nom de votre équipe
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
        front_left = sensors[sensor_front_left]
        front_right = sensors[sensor_front_right]
        left = sensors[sensor_left]
        right = sensors[sensor_right]

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

        # # robot 0 : braitenberg avoider
        # if self.robot_id == 0 or self.robot_id == 2 or self.robot_id == 1 or self.robot_id == 3 :
        #     # comportement deblocage
        #     if self.memory < 0:
        #         self.memory += 1
        #         translation = 0.2
        #         rotation = left - right + (random.random()-0.5)*0.15
        #         return translation, rotation, False
            
        #     # detection d'obstacle
        #     if front < 0.5:
        #         self.memory += 1
        #     else :
        #         self.memory = max(0, self.memory - 1)
            
        #     # si bloqué trop longtemps, activation déblocage
        #     if self.memory > 5:
        #         self.memory = -10  # activer mode déblocage 10 steps

        #     # comportement Braitenberg avoider
        #     translation = front*0.3 + 0.7
        #     rotation = 0.3*(1-front) + 0.4*(front_left - front_right) + 0.3*(left - right) + (random.random()-0.5)*0.2

        # robot 1 : robot stalker (braitenberg loveBot)
        if self.robot_id == 0 or self.robot_id == 2 or self.robot_id == 1 or self.robot_id == 3 :
            # Mode d’échappement : si mur ou robot très proche
            if self.memory < 0:
                self.memory += 1
                # translation minime pour que le robot puisse tourner
                translation = 0.05

                # si la distance entre la droite et la gauche pareille, tourne random
                if abs(left - right) < 0.05:
                    rotation = random.choice([-1, 1])
                # sinon, tourne vers là où il peut
                else:
                    if left < right:
                        rotation = -1
                    else:
                        rotation = 1

                return translation, rotation, False
            
            # détection d'obstacle
            if front < 0.5:
                self.memory += 1
            else :
                self.memory = max(0, self.memory - 1)
            
            # si bloqué trop longtemps, activation déblocage
            if self.memory > 5:
                self.memory = -10  # activer mode déblocage 10 steps
            
            # Niveau 1 : détection de robot adverse, le suivre
            # si robot détecté devant, devant à gauche ou devant à droite ET si c'est robot de l'équipe adverse
            elif ((sensor_to_robot[sensor_front] < 0.8 and sensor_team[sensor_front] != self.team_name) or
                  (sensor_to_robot[sensor_front_left] < 0.8 and sensor_team[sensor_front_left] != self.team_name) or
                  (sensor_to_robot[sensor_front_right] < 0.8 and sensor_team[sensor_front_right] != self.team_name)):
                
                # réinitialise memory à zéro
                self.memory = 0
                
                # avance lentement vers le robot ennemi détecté
                translation = sensor_to_robot[sensor_front] * 0.3 + 0.2 * (sensor_to_robot[sensor_front_left] + sensor_to_robot[sensor_front_right])
                
                # tourne vers le robot ennemi détecté
                rotation = (sensor_to_robot[sensor_front_right] - sensor_to_robot[sensor_front_left]) + 0.6 * (sensor_to_robot[sensor_right] - sensor_to_robot[sensor_left])
            
            # Niveau 2 : détection d’obstacle, l’éviter
            elif front < 0.8 or left < 0.6 or right < 0.6:
                # réinitialise memory à zéro
                self.memory = 0

                # avance en fonction de la distance entre l'obstacle et le robot
                translation = front*0.3 + 0.7
                
                # tourne à l'opposé de l'obstacle avec une petite déviation aléatoire
                rotation = 0.3*(1-front) + 0.5*(front_left - front_right) + 0.3*(left - right) + (random.random()-0.5)*0.2
            
            # Niveau 3 : comportement par défaut, l’exploration
            else:
                self.memory = 0
                # vitesse fixe
                translation = 1
                # déviation aléatoire
                rotation = (random.random() - 0.5) * 0.3

        return translation, rotation, False
