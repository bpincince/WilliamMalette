# --------------------------------------------------------
# Nom : William Mallette
# Titre : Question/Option
# Description : Un handler pour les questions, et par relation, les réponses à ces questions.
# --------------------------------------------------------

# - Importation des modules ------------------------------

from PIL import Image
from pygame import mixer
from modules.jeu.sprites import Collider
from modules.tuteur import questions, resultats, temps
from random import randrange, uniform

# - Variables globales -----------------------------------

# Listes globales, res ipsa loquitur
lettres = ["a", "b", "c", "d"]
positions = [(260, 280), (380, 280), (260, 360), (380, 360)]

# - Déclaration des fonctions ----------------------------

# import ne fonctionne pas trop bien avec les variables globales, donc j'ai crée un class pour les points
class Pointage:
    def __init__(self):
        self.points = 0

    def add(self, n):
        self.points += n

# Un class pour les options
class Option:
    def __init__(self, parent, question_obj, text, btn, pos, correct):
        # Garder le canvas
        self.parent = parent

        # Garder le question auquel l'option est parenté
        self.control = question_obj

        # Garder mettaton
        self.mtt = question_obj.mtt

        # Créer le bouton
        self.spr = Collider(parent, Image.open(f"images/boutons/{btn}.png"), question_obj.player, pos[0], pos[1], func=lambda: self.reponse(correct))

        # Le text
        if btn == "a" or btn == "c":
            self.text = parent.create_text(pos[0] - 40, pos[1], text=text, font=("Determination Mono", 20), fill="#FFFFFF", justify="right", anchor="e")
        else:
            self.text = parent.create_text(pos[0] + 40, pos[1], text=text, font=("Determination Mono", 20), fill="#FFFFFF", justify="left", anchor="w")

    # Handle les résultats
    def reponse(self, correct):
        # Fonction qui reset les objets pour le prochain question
        # C'est seulement ici puisque des lambda ne peuvent pas exécuter plus qu'un instruction
        def back():
            # Bouge MTT et change son animation
            self.mtt.move(1)
            self.mtt.setAnim(self.mtt.anim_wave)

            # Bouge le player et change le mode de son input
            self.control.UI.movePlayer()

            # Re-enable le collision du bouton de continuation
            self.control.UI.btnContinue.cancollide = True

            # Détruire ce qui reste
            self.mtt.msg.destroy()
            for option in self.control.options:
                option.parent.delete(option.text)

            self.control.UI.menuText("* Mettaton prépare un autre\n  question.")

        # Le correct réponse
        if correct:
            # Changer l'animation
            self.mtt.setAnim(self.mtt.anim_celebration)

            # Un message
            self.mtt.message("CORRECTE!!!", takeInput=False)

            # Changer le couleur du text à vert
            self.parent.itemconfig(self.text, fill="#008000")

            # Joue le gif de confetti
            self.mtt.confetti.Play(reset=True)

            # Heal le player
            self.control.player.heal(2)

            # Jouer le son
            s = mixer.Sound("sons/snd_won.wav")
            s.set_volume(0.15)
            s.play()

            # Ajouter un point
            points.add(1)
            # Si les points arrivent à un multiple de 5, level up!
            if points.points % 5 == 0:
                self.control.player.setLV(self.control.player.lv + 1)
                self.control.player.setHP(self.control.player.hp + 4)

            # Attendre et reset
            self.control.root.after(1700, back)
        else:
            # Changer le couleur du text à rouge
            self.parent.itemconfig(self.text, fill="#FF0000")

            # Dialogue
            self.mtt.message("INCORRECTE!!!", takeInput=False)

            # Commence le laser (voir MTT.laser)
            self.control.mtt.laser(back)

        # Compiler les résultats dans cette liste
        _resultats = []
        for i, option in enumerate(self.control.options):
            # Changer les texts des autres options à jaune
            if option != self:
                # Montrer le correct réponse en vert
                if i == self.control.correct - 1: option.parent.itemconfig(option.text, fill="#008000")
                # Pour les autres options
                else:
                    # S'ils sont gris, garder le gris.
                    if not option.parent.itemcget(option.text, "fill") == "#888888":
                        # Si non, jaune
                        option.parent.itemconfig(option.text, fill="#FFFF00")

            # Enlève les boutons
            option.spr.destroy()

            # Ajouter l'option (et son couleur) à la liste de résultats
            _resultats.append([option.parent.itemcget(option.text, 'text'), option.parent.itemcget(option.text, "fill")])
 
            # Si le timer arrive à 0, enlève les texts en même temps
            if correct is None:
                option.parent.delete(option.text)

        # Ajoute cette liste de résultats à la liste global de résultats
        resultats.append(_resultats)

        # Ajoute le temps à la liste
        temps.append(int(self.control.parent.itemcget(self.control.timer, "text")))

        # Enlève le timer
        self.control.timerexists = False
        self.control.parent.delete(self.control.timer)
        
        # Enlève le text d'indice et unbind 'c'
        self.control.parent.delete(self.control.txtIndice)
        self.control.root.unbind("<c>")
        
        # Enlève le text du question
        self.control.parent.delete(self.control.qtext)

# Class pour le question en général
class Question:
    def __init__(self, root, parent, player, mtt, ui, question, reponses, correct, time=30):
        # Garder le fenetre, canvas, player, mettaton, et le confetti
        self.root = root
        self.parent = parent
        self.player = player
        self.mtt = mtt
        self.UI = ui

        # Créer le text du question
        self.qtext = parent.create_text(200, 100, text=question, font=("Determination Mono", 20), fill="#FFFFFF", anchor="w", width=400)

        # Un fonction qui fait le text de question vibrer
        def shakeQuestion():
            # Deux offsets
            nx = round(uniform(-1, 1), 2)
            ny = round(uniform(-1, 1), 2)
            # Bouger le text
            parent.move(self.qtext, nx, ny)
            # Retourner à normal, répète
            root.after(30, lambda: parent.move(self.qtext, -nx, -ny))
            root.after(30, shakeQuestion)
        shakeQuestion()

        # Ajouter le question à la liste globale
        questions.append(question[9:len(question)])

        # Garder quel réponse est bien
        self.correct = correct

        def startTimer():
            # Les options
            self.options = []
            for i in range(len(reponses)):
                # Marque si l'option correspond à le correct réponse
                if i == correct - 1:
                    reponse = True
                else:
                    reponse = False
                # Créer l'option
                option = Option(parent, self, reponses[i], lettres[i], positions[i], reponse)
                option.spr.color((64, 255, 64, 255))
                self.options.append(option)

            # L'option d'un indice
            # Prévenir la suicide par indice
            if player.hp > 1:
                self.txtIndice = parent.create_text(320, 10, text="[Appuyez sur 'c' pour un indice (-1 HP)]",
                                                  fill="#AAAAAA", font=("Gulim", 11, "bold"))
                root.bind("<c>", lambda c: self.hint())
            # Il faut quand même créer un objet de text ici, puisque le programme va essayer de supprimer self.txtIndice plus tard
            else:
                self.txtIndice = parent.create_text(320, 10)

            # Le timer
            self.timer = parent.create_text(320, 280, text=str(time), font=("Determination Mono", 20), fill="#FF0000")
            self.timerexists = True
            root.after(500, self.updateTimer)

            # Permettre le mouvement
            player.bindInput(mode="arena")

        # Après un moment, montre les options et commence le timer
        root.after(1500, startTimer)

    # Élimine deux options incorrects
    def hint(self):
        # Deux nombres, correspondant à des indexes de self.options
        n1 = -1
        n2 = -1

        # Sélectionner deux au hasard, qui sont uniques et ne correspondent pas à la correct réponse
        while n1 == -1 or n1 == self.correct - 1:
            n1 = randrange(0, 4)
        while n2 == -1 or n2 == self.correct - 1 or n2 == n1:
            n2 = randrange(0, 4)

        # Effectue des changements aux options sélectionnés
        for i, option in enumerate(self.options):
            if i == n1 or i == n2:
                # Change le couleur de l'option à gris, et enlève l'habileté de le choisir
                option.spr.color((128, 128, 128, 255))
                self.parent.itemconfig(option.text, fill="#888888")
                option.spr.cancollide = False

        # Jouer un son
        s = mixer.Sound("sons/enemydust.wav")
        s.set_volume(0.125)
        s.play()

        # Dommager le player
        self.player.hurt(1, shake=False)

        # Cache le text d'indice
        self.parent.itemconfig(self.txtIndice, text="")

        # Unbind le clé c pour prévenir un deuxième indice
        self.root.unbind("<c>")

    # Changer le timer
    def updateTimer(self):
        if self.timerexists:
            curr = self.parent.itemcget(self.timer, 'text')
            # Enlèver 1 du timer chaque seconde jusqu'à temps qu'il soit 0
            if curr != "0":
                self.parent.itemconfig(self.timer, text=str(int(curr)-1))
                self.root.after(500, self.updateTimer)
            # Lorsque le timer est 0, traite-la comme un mauvaise réponse
            else:
                self.options[0].reponse(None)

# - Programme principal ----------------------------------

# Les points
points = Pointage()