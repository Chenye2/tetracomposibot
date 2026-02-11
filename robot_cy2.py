import math
from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "on est le premier"  # vous pouvez modifier le nom de votre équipe
    robot_id = -1             # ne pas modifier. Permet de connaitre le numéro de votre robot.
    memory = 0                # vous n'avez le droit qu'a une case mémoire qui doit être obligatoirement un entier

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
        rear_left = sensors[sensor_rear_left]
        rear_right = sensors[sensor_rear_right]

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

        bestParam = [1, 0, 1, 1, -1, 1, 1, -1]

        # ----------------------------------------------------------------------------------------
        # Mode débloquage : activé si bloqué depuis 5 steps
        if self.memory >= 5:
            translation = -front  # reculer
            rotation = 1 if front_left > front_right else -1
            self.memory = 0  # reset
            print("========== DEBLOCAGE ==========")
            return translation, rotation, False
        
        # ----------------------------------------------------------------------------------------
        # NIVEAU 1 : HATE WALL
        dist_wall = min(
                sensor_to_wall[sensor_front],
                sensor_to_wall[sensor_front_left],
                sensor_to_wall[sensor_front_right]
            )
        if dist_wall < 0.2:

            # dist_wall_left : distance au mur le plus proche du coté gauche du robot (0 -> mur proche, 1 -> mur loin)
            dist_wall_left = min(sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_left], sensor_to_wall[sensor_rear_left])
            # dist_wall_right : distance au mur le plus proche du coté droit du robot
            dist_wall_right = min(sensor_to_wall[sensor_front_right], sensor_to_wall[sensor_right], sensor_to_wall[sensor_rear_right])
            
            # si un mur est très proche, on l'évite
            if dist_wall_left < 0.2 or dist_wall_right < 0.2:
                translation = -0.3
                if dist_wall_left < dist_wall_right:
                    rotation = -1.0 # tourner à droite
                else:
                    rotation = 1.0 # tourner à gauche
                print("HATE WALL 1111")
            # sinon, on évite les murs de manière plus douce
            else :
                translation = sensor_to_wall[sensor_front]
                rotation = (
                    sensor_to_wall[sensor_front_left] +
                    sensor_to_wall[sensor_left] +
                    sensor_to_wall[sensor_front_right] -
                    sensor_to_wall[sensor_right] -
                    random.uniform(-0.5, 0.5)
                )
                rotation = max(-1.0, min(1.0, rotation))
                print("HATE WALL 222222222222222")
            
            # -------- MISE A JOUR DE LA MEMOIRE DEBLOQUAGE --------
            if dist_wall < 0.35:
                self.memory += 1
            else :
                self.memory = max(0, self.memory - 1)
            
            return translation, rotation, False 
            
        # ----------------------------------------------------------------------------------------
        # NIVEAU 2 : HATE BOT
        dist_robot = min(
                sensor_to_robot[sensor_front],
                sensor_to_robot[sensor_front_left],
                sensor_to_robot[sensor_front_right],
            )
        if dist_robot < 0.2:
            dist_robot_left = min(
                sensor_to_robot[sensor_front_left],
                sensor_to_robot[sensor_left],
                sensor_to_robot[sensor_rear_left]
            ) # coté gauche du robot
            dist_robot_right = min(
                sensor_to_robot[sensor_front_right],
                sensor_to_robot[sensor_right],
                sensor_to_robot[sensor_rear_right]
            ) # coté droit du robot

            near_teammate = False  # true si un robot de la même équipe est détecté par les senseurs
            for i in range(8): # on parcourt les 8 senseurs
                # On ignore les senseurs qui ne voient aucun robot / qui voient un mur
                if sensor_team[i] is not None:
                    # si le senseur voit un robot de meme équipe, on note true dans near_teammate
                    if sensor_team[i] == self.team_name:
                        near_teammate = True
           
            # CAS 1 : si le robot proche est un allié, on l'évite
            if near_teammate:
                translation = -0.5
                rotation = dist_robot_left - dist_robot_right + random.uniform(-0.5, 0.5)
                print("--------------------HATE BOT 2222222222222222")
            # CAS 2 : si un robot est très proche, on l'évite
            # if dist_robot_left < 0.3 or dist_robot_right < 0.3 : 
            else :
                translation = 0
                # le danger est du coté gauche -> tourner à droite
                if dist_robot_left < dist_robot_right : 
                    rotation = -1.0 # tourner à droite
                else: 
                    rotation = 1.0 # tourner à gauche
                # rotation = dist_robot_right - dist_robot_left + (random.random()-0.5)*0.15
                print("--------------------HATE BOT 11111")
            # CAS 3 : sinon (le robot proche est adversaire) on le bloque
            # else :
            #     translation = 0.5
            #     rotation = dist_robot_right - dist_robot_left + random.uniform(-0.25, 0.25)
            rotation += 0.3 * (1 if self.memory % 2 == 0 else -1)
            rotation = max(-1.0, min(1.0, rotation))

            # -------- MISE A JOUR DE LA MEMOIRE DEBLOQUAGE --------
            if dist_robot < 0.35:
                self.memory += 1
            else :
                self.memory = max(0, self.memory - 1)

            return translation, rotation, False
        

        # ----------------------------------------------------------------------------------------
        # NIVEAU 3 : COMPORTEMENT PAR DEFAUT
        # robot 0 : comportement optimisé par genetic algorithm
        if self.robot_id == 0 :
            translation = math.tanh ( bestParam[0] + bestParam[1] * front_left + bestParam[2] * front + bestParam[3] * front_right )
            rotation = math.tanh ( bestParam[4] + bestParam[5] * front_left + bestParam[6] * front + bestParam[7] * front_right )
        # robot 1 : braitenberg
        elif self.robot_id == 1 or self.robot_id == 2:
            translation = front*0.3 + 0.7
            rotation = 0.2*(1-front) + 0.3*(front_left - front_right) + 0.3*(left - right) + (random.random()-0.5)*0.2
        # les autres robots avancent tout droit
        else :
            translation = 1.0
            rotation = 0.0
        
        # -------- MISE A JOUR DE LA MEMOIRE DEBLOQUAGE --------
        danger = min(front, front_left, front_right, left, right)
        # le robot essaie d'avancer mais obstacle devant -> blocage
        if danger < 0.35 and translation > 0:
            self.memory += 1
        else :
            self.memory = max(0, self.memory - 1)

        print("------------------------------------------------------------COMPORTEMENT PAR DEFAUT")
        return translation, rotation, False
