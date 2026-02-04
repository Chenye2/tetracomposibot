
from robot import * 
import math

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "RandomSearch2"
    robot_id = -1
    iteration = 0

    param = [] # stratégie courante
    bestParam = [] # meilleure statégie
    it_per_evaluation = 400
    trial = 0 # numéro d'évaluation

    score = 0  # score courant
    bestScore = 0
    bestTrial = -1 

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
        self.it_per_evaluation = it_per_evaluation

        # Exo 4
        # initialise le fichier
        with open("randomsearch2.txt", "w") as f :
            pass

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
                    #print("current eval : ", self.current_eval)
                    #print("somme score : ", self.sum_score)

                    # reset le score à 0 pour calculer la prochaine evaluation
                    self.score = 0

                    # si on n'a pas encore fini les 3 evaluations
                    if self.current_eval < self.nb_repeat :
                        self.iteration += 1 
                        return 0, 0, True
                    
                    # fin des 3 evaluations
                    # sauvegarde la meilleure stratégie
                    if self.sum_score > self.bestScore:
                         self.bestScore = self.sum_score
                         self.bestParam = self.param.copy()
                         self.bestTrial = self.trial
                         print("NEW BEST SCORE :", self.bestScore)

                    # Exo 4 
                    # on sauvegarde les résultats de cette tentative
                    with open("randomsearch2.txt", "a") as f :
                        f.write(f"{self.trial}, {self.sum_score}, {self.bestScore}\n")

                    print ("\tparameters           =",self.param)
                    print ("\ttranslations         =",self.log_sum_of_translation,"; rotations =",self.log_sum_of_rotation) # *effective* translation/rotation (ie. measured from displacement)
                    print ("\tdistance from origin =",math.sqrt((self.x-self.x_0)**2+(self.y-self.y_0)**2))
                    print ("\ttotal score                =", self.sum_score)

                # fin de recherche : rejouer la meilleur stratégie
                if self.trial >= self.max_trials:
                    print("\n=== END OF SEARCH ===")
                    print("Best score :", self.bestScore)
                    print("Best params:", self.bestParam)
                    self.param = self.bestParam.copy()
                    self.replay_best = True
                    self.iteration = 0
                    self.it_per_evaluation = 1000
                # sinon continue la recherche
                else :
                    self.param = [random.randint(-1, 1) for i in range(8)]
                    self.trial = self.trial + 1
                    print ("Trying strategy no.",self.trial)
                
                self.current_eval = 0
                self.sum_score = 0
                self.iteration += 1 
                return 0, 0, True # ask for reset
        
        # rejouer la meilleure stratégie à l'infini
        if self.replay_best and self.iteration >= self.it_per_evaluation :
            #print ("\n\tparameters           =",self.param)
            #print ("\ttranslations         =",self.log_sum_of_translation,"; rotations =",self.log_sum_of_rotation) # *effective* translation/rotation (ie. measured from displacement)
            #print ("\tdistance from origin =",math.sqrt((self.x-self.x_0)**2+(self.y-self.y_0)**2))
            #print ("\tscore                =", self.score)
            self.iteration = 1
            return 0, 0, True
        
        # fonction de contrôle (qui dépend des entrées sensorielles, et des paramètres)
        translation = math.tanh ( self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right] )
        rotation = math.tanh ( self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right] )

        # calcule la translation et la rotation effective instantanée
        delta_translation = self.log_sum_of_translation - self.prev_translation
        delta_rotation = self.log_sum_of_rotation - self.prev_rotation

        self.score += delta_translation * (1 - abs(delta_rotation))

        # on stocke les valeurs de cette itération
        self.prev_translation = self.log_sum_of_translation
        self.prev_rotation = self.log_sum_of_rotation

        self.iteration = self.iteration + 1        

        return translation, rotation, False
