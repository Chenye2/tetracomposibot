
from robot import * 
import math

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "GeneticAlgorithms"
    robot_id = -1
    iteration = 0

    param = [] # stratégie courante

    parent_param = [] # stratégie du parent

    it_per_evaluation = 400
    trial = 0 # numéro d'évaluation

    score = 0  # score courant

    # pour chaque statégie
    current_eval = 0  # nombre d'evaluation effectué = {0, 1, 2}
    nb_repeat = 3  # nombre total d'evaluation à effectuer
    sum_score = 0  # somme des scores

    # pour calculer les deltas effectifs
    prev_translation = 0
    prev_rotation = 0

    replay_best = False
    max_trials = 100 # nombre max de stratégies à evaluer

    x_0 = 0
    y_0 = 0
    theta_0 = 0 # in [0,360]

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a",evaluations=0,it_per_evaluation=0):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots+=1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0

        self.param = [random.randint(-1, 1) for i in range(8)]

        # Initialisation : le parent est lui-même
        self.parent_param = self.param.copy()

        self.it_per_evaluation = it_per_evaluation
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def reset(self):
        super().reset()

        self.theta = random.uniform(-180, 180)  # orientation aléatoire

        self.score = 0
        self.prev_translation = 0
        self.prev_rotation = 0

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):

        if self.iteration % self.it_per_evaluation == 0 and (not self.replay_best):
            if self.iteration > 0:
                # ajoute le score de cette evaluation et incrémente le compteur
                self.sum_score += self.score
                self.current_eval += 1

                # reset le score à 0 pour calculer la prochaine evaluation
                self.score = 0

                # si on n'a pas encore fini les 3 evaluations
                if self.current_eval < self.nb_repeat :
                    self.iteration += 1 
                    return 0, 0, True
                
                # fin des 3 evaluations

                # cas particulier : premier essai (Trial 0)
                if self.trial == 0:
                    self.parent_score = self.sum_score
                    print("Initialisation - Score Parent:", self.parent_score)
                else:
                    # comparaison Enfant vs Parent
                    if self.sum_score > self.parent_score:
                        print("Trial", self.trial, ": ENFANT GAGNE", self.sum_score, ">", self.parent_score)
                        self.parent_score = self.sum_score
                        self.parent_param = self.param.copy()
                    else:
                        if debug: print("Trial", self.trial, ": Enfant rejeté", self.sum_score)

                # vérification de la fin de l'expérience
                if self.trial >= self.max_trials:
                    print("\n=== FIN DE L'ÉVOLUTION ===")
                    print("Meilleurs paramètres :", self.parent_param)
                    print("Meilleurs scores :", self.parent_score)
                    self.param = self.parent_param.copy()
                    self.replay_best = True
                    self.iteration = 1
                    self.it_per_evaluation = 1000
                    return 0, 0, True

                # phase de mutation pour créer un nouvel enfant
                self.param = self.parent_param.copy()
                
                # choix d'un gène au hasard
                gene_idx = random.randint(0, 7)
                old_val = self.param[gene_idx]
                
                # mutation sans retirage (valeur forcément différente)
                possible_values = [-1, 0, 1]
                possible_values.remove(old_val)
                self.param[gene_idx] = random.choice(possible_values)
                
                # reset des compteurs pour le prochain individu (le mutant)
                self.trial += 1
                self.current_eval = 0
                self.sum_score = 0
                self.iteration += 1 
                return 0, 0, True 

        # mode Replay pour montrer le résultat final
        if self.replay_best and self.iteration >= self.it_per_evaluation :
            self.iteration = 1
            return 0, 0, True
        
        # fonction de contrôle (qui dépend des entrées sensorielles, et des paramètres)
        translation = math.tanh(self.param[0] + self.param[1]*sensors[sensor_front_left] + self.param[2]*sensors[sensor_front] + self.param[3]*sensors[sensor_front_right])
        rotation = math.tanh(self.param[4] + self.param[5]*sensors[sensor_front_left] + self.param[6]*sensors[sensor_front] + self.param[7]*sensors[sensor_front_right])

        # calcule la translation et la rotation effective instantanée
        delta_trans = self.log_sum_of_translation - self.prev_translation
        delta_rot = self.log_sum_of_rotation - self.prev_rotation

        self.score += delta_trans * (1 - abs(delta_rot))

        self.prev_translation = self.log_sum_of_translation
        self.prev_rotation = self.log_sum_of_rotation

        self.iteration += 1        
        return translation, rotation, False
