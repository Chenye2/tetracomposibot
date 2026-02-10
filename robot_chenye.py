import math
from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "Chenye"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

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
        
        front = sensors[sensor_front]
        front_left = sensors[sensor_front_left]
        front_right = sensors[sensor_front_right]
        left = sensors[sensor_left]
        right = sensors[sensor_right]

        # robot 0 : braitenberg avoider
        if self.robot_id == 3 :
            # comportement deblocage
            if self.memory < 0:
                self.memory += 1
                translation = 0.05
                rotation = left - right + (random.random()-0.5)*0.15
                return translation, rotation, False
            
            # detection d'obstacle
            if front < 0.5:
                self.memory += 1
            else :
                self.memory = max(0, self.memory - 1)
            
            # si bloqué trop longtemps, activation déblocage
            if self.memory > 5:
                self.memory = -10  # activer mode déblocage 10 steps

            # comportement Braitenberg avoider
            translation = front*0.3 + 0.7
            rotation = 0.3*(1-front) + 0.4*(front_left - front_right) + 0.3*(left - right) + (random.random()-0.5)*0.2


        # robot 1 : genetic algorithm
        if self.robot_id == 0 or self.robot_id == 1 or self.robot_id == 2:
            # statégie optimisée simulée
            # bestParam = [1, 1, -1, 1, -1, 1, 1, -1] # score 869
            bestParam = [1, 0, 1, 1, -1, 1, 1, -1] # score 976
            
            near_wall = max(
                1 - sensor_to_wall[sensor_front],
                1 - sensor_to_wall[sensor_front_left],
                1 - sensor_to_wall[sensor_front_right],
                1 - sensor_to_wall[sensor_left],
                1 - sensor_to_wall[sensor_right]
            )

            near_robot = max(
                1 - sensor_to_robot[sensor_front],
                1 - sensor_to_robot[sensor_front_left],
                1 - sensor_to_robot[sensor_front_right],
            )
            
            robot_stuck = sensor_to_robot[sensor_front] < 0.6 and sensor_to_wall[sensor_front] > 0.7

            # si le robot est coincé trop longtemps, on active une stratégie de débloquage
            if self.memory > 10: 
                print("---------------------- DEBLOCAGE -------------------")
                if sensor_to_wall[sensor_front] < sensor_to_robot[sensor_front]:
                    translation = 0.3
                    rotation = sensor_to_wall[sensor_left] - sensor_to_wall[sensor_right] + (random.random()-0.5)
                else:
                    translation = 0.2
                    rotation = sensor_to_robot[sensor_left] - sensor_to_robot[sensor_right] + (random.random()-0.5)
                self.memory = 0
            
            elif robot_stuck:
                translation = 0.2
                rotation = 1.0 if self.robot_id % 2 == 0 else -1.0
                self.memory = 0

            # hate wall
            elif near_wall > 0.4 :
                print("Subsomption : HATE WALL")
                translation = sensor_to_wall[sensor_front] * 0.3 + 0.6
                rotation = (
                    0.2 * (1 - sensor_to_wall[sensor_front]) + 
                    0.4 * (sensor_to_wall[sensor_front_left] - sensor_to_wall[sensor_front_right]) + 
                    0.4 * (sensor_to_wall[sensor_left] - sensor_to_wall[sensor_right]) + 
                    (random.random()-0.5)*0.2
                )
            
            # hate bot
            elif near_robot > 0.4 :
                print("Subsomption : HATE BOT")
                translation = sensor_to_robot[sensor_front] * 0.3 + 0.6
                rotation = (
                    0.2 * (1 - sensor_to_robot[sensor_front]) + 
                    0.4 * (sensor_to_robot[sensor_front_left] - sensor_to_robot[sensor_front_right]) + 
                    0.4 * (sensor_to_robot[sensor_left] - sensor_to_robot[sensor_right]) + 
                    (random.random()-0.5)*0.2
                )
            
            # comportement optimisé par genetic algorithm
            else :
                print("Genetic algorithm")
                translation = math.tanh ( bestParam[0] + bestParam[1] * front_left + bestParam[2] * front + bestParam[3] * front_right )
                rotation = math.tanh ( bestParam[4] + bestParam[5] * front_left + bestParam[6] * front + bestParam[7] * front_right )
            
            danger = max(near_wall, near_robot)
            if translation > 0.4 and danger > 0.5 : # si le robot avance trop lentement, on considère qu'il est bloqué
                self.memory += 1
            else:
                self.memory = max(0, self.memory - 1)
                

        return translation, rotation, False
