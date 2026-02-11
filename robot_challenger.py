# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Chenye LIN 21303883
#  Prénom Nom No_étudiant/e : Loïs ZHU 21303169
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

import math
from robot import * 

nb_robots = 0

class Robot_player(Robot):

    team_name = "SÉPADELIA"  # vous pouvez modifier le nom de votre équipe
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

        if self.robot_id == 0 or self.robot_id == 1 or self.robot_id == 2 :
            # ----------------------------------------------------------------------------------------
            # Mode débloquage
            # si le robot est considéré bloqué pendant 5 steps :
            # on force un comportement de sortie : recule + tourne du côté le plus libre
            if self.memory >= 5:
                translation = -front  # reculer
                rotation = 1 if front_left > front_right else -1
                self.memory = 0  # reset
                return translation, rotation, False
            
            # ----------------------------------------------------------------------------------------
            # NIVEAU 1 : HATE WALL
            dist_wall = min(
                    sensor_to_wall[sensor_front],
                    sensor_to_wall[sensor_front_left],
                    sensor_to_wall[sensor_front_right]
                )
            # si un mur est très proche devant
            if dist_wall < 0.2:

                # distance minimale côté gauche du robot
                dist_wall_left = min(sensor_to_wall[sensor_front_left], sensor_to_wall[sensor_left], sensor_to_wall[sensor_rear_left])
                # distance minimale côté droit du robot
                dist_wall_right = min(sensor_to_wall[sensor_front_right], sensor_to_wall[sensor_right], sensor_to_wall[sensor_rear_right])
                
                # cas 1 : coin front + left
                # mur devant et sur la gauche : recule et tourne à droite
                if sensor_to_wall[sensor_front_left] < 0.3 and sensor_to_wall[sensor_left] < 0.2:
                    translation = -0.2
                    rotation = -1.0
                # cas 2 : coin front + right
                # mur devant et sur la droite : recule et tourne à gauche
                elif sensor_to_wall[sensor_front_left] < 0.3 and sensor_to_wall[sensor_right] < 0.2:
                    translation = -0.2
                    rotation = 1.0
                # cas 3 : mur proche sur un coté
                # si un des deux côtés est plus proche : tourne vers le côté le plus libre
                elif dist_wall_left < 0.2 or dist_wall_right < 0.2:
                    translation = -0.2
                    if dist_wall_left < dist_wall_right:
                        rotation = -0.5 # tourner à droite
                    else:
                        rotation = 0.5 # tourner à gauche
                # sinon, on évite les murs de manière plus douce
                else :
                    translation = sensor_to_wall[sensor_front]
                    # calcul du "danger" sur gauche et droite
                    danger_left = (1 - sensor_to_wall[sensor_front_left]) + (1 - sensor_to_wall[sensor_left]) + 0.5*(1 - sensor_to_wall[sensor_rear_left])
                    danger_right = (1 - sensor_to_wall[sensor_front_right]) + (1 - sensor_to_wall[sensor_right]) + 0.5*(1 - sensor_to_wall[sensor_rear_right])
                    # tourne du côté le moins dangereux
                    rotation = -1.0 if danger_left > danger_right else 1.0
                
                # -------- incrément mémoire --------
                self.memory += 1

                return translation, rotation, False 
                
            # ----------------------------------------------------------------------------------------
            # NIVEAU 2 : HATE BOT
            # distance minimale robot-robot du coté front
            dist_robot = min(
                    sensor_to_robot[sensor_front],
                    sensor_to_robot[sensor_front_left],
                    sensor_to_robot[sensor_front_right]
                )
            if dist_robot < 0.2:
                # calcul du danger robot à gauche
                danger_robot_left = (
                    1 - sensor_to_robot[sensor_front_left] +
                    1 - sensor_to_robot[sensor_left] + 
                    1 - sensor_to_robot[sensor_rear_left]
                )
                # calcul du danger robot à droite
                danger_robot_right = (
                    1 - sensor_to_robot[sensor_front_right] +
                    1 - sensor_to_robot[sensor_right] +
                    1 - sensor_to_robot[sensor_rear_right]
                )

                near_teammate = False  # true si un robot de la même équipe est détecté par les senseurs
                for i in range(8): # on parcourt les 8 senseurs
                    # On ignore les senseurs qui ne voient aucun robot / qui voient un mur
                    if sensor_team[i] is not None:
                        # si le senseur voit un robot de meme équipe, on note true dans near_teammate
                        if sensor_team[i] == self.team_name:
                            near_teammate = True
            
                # CAS 1 : si le robot proche est un allié : tourner vers le côté le plus libre
                if near_teammate:
                    translation = -0.2
                    rotation = 1.0 if danger_robot_left < danger_robot_right else -1.0
                # CAS 2 : adversaire
                else :
                    translation = 0.1
                    rotation = danger_robot_right - danger_robot_left + (random.random()-0.5)

                # -------- incrément mémoire --------
                self.memory += 1

                return translation, rotation, False
            

            # ----------------------------------------------------------------------------------------
            # NIVEAU 3 : COMPORTEMENT PAR DEFAUT
            # robot 0 : comportement optimisé par genetic algorithm
            if self.robot_id == 0 :
                translation = math.tanh ( bestParam[0] + bestParam[1] * front_left + bestParam[2] * front + bestParam[3] * front_right )
                rotation = math.tanh ( bestParam[4] + bestParam[5] * front_left + bestParam[6] * front + bestParam[7] * front_right )
            # robot 1 et 2 : braitenberg
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
            if danger < 0.3 and translation > 0:
                self.memory += 1
            # sinon on décrémente progressivement
            else :
                self.memory = max(0, self.memory - 1)

            return translation, rotation, False


        # ================================== ROBOT SUIVEUR =======================================
        if self.robot_id == 3 :
            # Mode débloquage : activé si bloqué depuis 5 steps
            if self.memory >= 5:
                # réinitialisation de la mémoire et recul
                self.memory = 0  
                translation = -sensors[sensor_front]

                if left < right:
                    rotation = -1 
                else:
                    rotation = 1

                return translation, rotation, False

            # détection d'obstacle
            if front < 0.4 or front_left < 0.3 or front_right < 0.3:
                self.memory += 1
            else :
                self.memory = max(0, self.memory - 1)


            # Niveau 2 : détection de robot adverse, le suivre
            # si robot détecté devant, devant à gauche ou devant à droite ET si c'est robot de l'équipe adverse
            if ((sensor_to_robot[sensor_front] < 0.8 and sensor_team[sensor_front] != self.team_name) or
                  (sensor_to_robot[sensor_front_left] < 0.8 and sensor_team[sensor_front_left] != self.team_name) or
                  (sensor_to_robot[sensor_front_right] < 0.8 and sensor_team[sensor_front_right] != self.team_name)):

                # avance lentement vers le robot ennemi détecté
                translation = sensor_to_robot[sensor_front] * 0.4 + 0.2

                # tourne vers le robot ennemi détecté
                rotation = ((sensor_to_robot[sensor_front_right] - 
                             sensor_to_robot[sensor_front_left]) + 
                            (sensor_to_robot[sensor_right] - 
                             sensor_to_robot[sensor_left]) +
                            (sensor_to_robot[sensor_rear_right] -
                             sensor_to_robot[sensor_rear_left]))
                
                return translation, rotation, False
            
            # Niveau 3 : détection d’obstacle, l’éviter
            elif front < 0.6 or left < 0.6 or right < 0.6:

                # avance en fonction de la distance entre l'obstacle et le robot
                translation = front*0.3 + 0.4
                # tourne à l'opposé de l'obstacle avec une déviation aléatoire
                rotation = (
                    sensors[sensor_front_left] +
                    sensors[sensor_left] +
                    sensors[sensor_rear_left] -
                    sensors[sensor_front_right] -
                    sensors[sensor_right] -
                    sensors[sensor_rear_right] +
                    random.uniform(-0.5, 0.5)
                )
                
                return translation, rotation, False
            
            # Niveau 4 : comportement par défaut, l’exploration
            # vitesse rapide fixe
            translation = 1
            # déviation aléatoire
            rotation = (random.random() - 0.5) * 0.3

        
        return translation, rotation, False


