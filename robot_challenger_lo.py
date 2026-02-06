# Projet "robotique" IA&Jeux 2025
#
# Binome:
#  Prénom Nom No_étudiant/e : Chenye LIN 21303883
#  Prénom Nom No_étudiant/e : Loïs ZHU 21303169
#
# check robot.py for sensor naming convention
# all sensor and motor value are normalized (from 0.0 to 1.0 for sensors, -1.0 to +1.0 for motors)

from robot import * 
import math
import random

nb_robots = 0

class Robot_player(Robot):

    team_name = "SixSeven"  # Nom d'équipe
    robot_id = -1             # Identifiant unique
    memory = 0                # Variable mémoire (compteur ou état)

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        super().__init__(x_0, y_0, theta_0, name="Robot "+str(self.robot_id), team=self.team_name)

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        translation = 1.0 # Vitesse par défaut (toujours à fond)
        rotation = 0.0
        
        # ROBOT 0 : L'ATTAQUANT / HARCELEUR
        # Il scanne les alentours pour trouver l'ennemi le plus proche
        if self.robot_id == 0:
            
            # 1. ANALYSE : On cherche l'ennemi le plus proche
            meilleure_cible_dist = -1
            meilleure_cible_idx = -1
            
            if sensor_robot is not None and sensor_team is not None:
                nb_sensors = len(sensors)
                for i in range(nb_sensors):
                    # Si c'est un robot ET qu'il n'est pas de mon équipe
                    if sensor_robot[i] == 1 and sensor_team[i] != self.team_name:
                        # On cherche celui qui est le plus près (valeur sensor élevée = proche)
                        if sensors[i] > meilleure_cible_dist:
                            meilleure_cible_dist = sensors[i]
                            meilleure_cible_idx = i

            # 2. ACTION : ATTAQUE OU CHASSE
            if meilleure_cible_idx != -1:
                # --- CAS A : ENNEMI REPÉRÉ (MODE TAUREAU) ---
                translation = 1.0 
                
                # Logique de rotation binaire pour braquer vers l'ennemi
                mid_sensor = len(sensors) // 2 
                
                if meilleure_cible_idx < mid_sensor:
                    rotation = -0.8 # Tourne à GAUCHE (Fort)
                elif meilleure_cible_idx > mid_sensor:
                    rotation = 0.8  # Tourne à DROITE (Fort)
                else:
                    rotation = 0    # Droit devant !
                    
            else:
                # --- CAS B : PERSONNE EN VUE (MODE CHASSE) ---
                # Il avance vite en faisant des S (oscillation) pour scanner la zone.
                
                translation = 1.0 
                
                # Evitement simple des murs
                evitement = (sensors[sensor_front_left] - sensors[sensor_front_right])
                
                # Oscillation sinusoïdale basée sur la mémoire
                oscillation = math.cos(self.memory * 0.1) * 0.2 
                self.memory += 1 
                
                rotation = evitement + oscillation

        # ROBOTS 1 & 2 : LES EXPLORATEURS 
        elif self.robot_id == 1 or self.robot_id == 2:
            # j'ai pris les paramètres de randomsearch2 (scores : 703)
            p = [0, -1, 1, 1, -1, 1, 1, -1] 

            translation = math.tanh(p[0] + p[1]*sensors[sensor_front_left] + p[2]*sensors[sensor_front] + p[3]*sensors[sensor_front_right])
            rotation = math.tanh(p[4] + p[5]*sensors[sensor_front_left] + p[6]*sensors[sensor_front] + p[7]*sensors[sensor_front_right])

        # ROBOT 3 : LE DÉFENSEUR (LONGE-MUR / NETTOYEUR)
        # Utilise une machine à états (Memory) pour ne jamais se coincer
        else:
            # self.memory agit comme un "Timer" ici
            
            if self.memory > 0:
                # ETAT 1 : Mode Dégagement (on recule pendant X tours)
                translation = -0.5
                rotation = 1.0 # Demi-tour
                self.memory -= 1
            
            else:
                # ETAT 0 : Mode Normal
                
                # Si mur en face trop proche -> On passe en Mode Dégagement
                if sensors[sensor_front] < 0.3:
                    self.memory = 10 # On initialise le timer à 10
                    translation = 0
                
                else:
                    # Stratégie : Garder le mur à sa DROITE
                    dist_mur_droite = sensors[sensor_right]
                    
                    translation = 0.8 # Vitesse modérée pour bien couvrir
                    
                    if dist_mur_droite < 0.2: # Trop près du mur
                        rotation = 0.3 # S'éloigne
                    elif dist_mur_droite > 0.8: # Trop loin (ou pas de mur)
                        rotation = -0.4 # Cherche le mur
                    else:
                        rotation = 0 # Parfait

        

        return translation, rotation, False