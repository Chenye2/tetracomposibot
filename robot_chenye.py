import math
from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "Chenye"  # vous pouvez modifier le nom de votre équipe
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

        # robot 0 : braitenberg avoider + subsomption (ou po)
        if self.robot_id == 0 or self.robot_id == 1 or self.robot_id == 2 or self.robot_id == 3:
            translation = front*0.3 + 0.7
            rotation = 0.3*(1-front) + 0.4*(front_left - front_right) + 0.3*(left - right) + (random.random()-0.5)*0.2


        # robot 1 : braitenberg + subsomption (si trop longtemps sans avancer : forcer tourner)
        # elif self.robot_id == 1:
            
        
        # robot 2 : competement optimisé par genetic algorithm
        elif self.robot_id == 1 or self.robot_id == 2:
            translation = math.tanh ( self.bestParam[0] + self.bestParam[1] * sensors[sensor_front_left] + self.bestParam[2] * sensors[sensor_front] + self.bestParam[3] * sensors[sensor_front_right] )
            rotation = math.tanh ( self.bestParam[4] + self.bestParam[5] * sensors[sensor_front_left] + self.bestParam[6] * sensors[sensor_front] + self.bestParam[7] * sensors[sensor_front_right] )

        # robot 3 :comportement Braitenberg optimisé
        else:
            # memory alterne entre 0 et 1 pour changer de comportement tous les 50 tours
            if self.memory >= 50:
                self.memory = 0
            else:
                self.memory += 1

            if self.memory < 25:
                # comportement défensif : recule si robot ou mur devant
                if sensor_view and (sensor_view[sensor_front] == 1 or (sensor_view[sensor_front] == 2 and sensor_team[sensor_front] != self.team_name)):
                    translation = -0.3  # reculer doucement
                    rotation = 0.5      # tourner pour éviter
                else:
                    translation = 0.3
                    rotation = 0
            else:
                # comportement offensif : avancer droit avec rotation aléatoire modérée
                translation = 0.5
                rotation = (random.random() - 0.5) * 0.3


        return translation, rotation, False
