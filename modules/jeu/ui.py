# --------------------------------------------------------
# Nom : William Mallette
# Titre : UI
# Description : Contrôle les autres aspects du jeu; les boutons et le text d'entre-question
# --------------------------------------------------------

# - Importation des modules ------------------------------

from modules.jeu.sprites import Collider, Sprite
from modules.jeu.dialogue import Dialogue
from modules.jeu.question import Question, points
from modules.tuteur import compileExpression, FormatNombre, questions, resultats, temps
from PIL import Image
from pygame import mixer
from random import randrange, uniform
from math import floor

# - Variables globales -----------------------------------

x = 10
y = 10
curr_page = 0

# - Déclaration des fonctions ----------------------------

# Fonction qui commence l'écran du fin
def compileResults(UI, skipFade=False):
    # Petit segment de code qui remplis les listes avec des questions impostor ඞ, pour tester les pages
    if False:
        global questions
        global resultats
        global temps
        questions = []
        resultats = []
        temps = [30] * 100
        for i in range(100):
            questions.append(str(i))
            resultats.append([[str(i), "#FFFFFF"]] * 4)

    # S'il y avait une question
    if len(questions) > 0:
        canvas = UI.parent
        # Bouger le player et prévenir le mouvement
        UI.player.move(y=900)
        UI.player.bindInput()
        # Arrêter Mettaton, changer son couleur à gris
        UI.mtt.animate = False
        UI.mtt.corps.color((128, 128, 128, 255))
        UI.mtt.bras.color((128, 128, 128, 255))

        # Une liste d'objets qui bouge
        movables = []

        # Montrer les résultats
        def showResults():
            # x et y sont des variables de positionnement globales
            global x
            global y
            # Les keybinds
            UI.root.bind("<Right>", lambda r: changePage("r"))
            UI.root.bind("<Left>", lambda l: changePage("l"))

            # Pour chaque question:
            for i, question in enumerate(questions):
                # Changer de page après chaque 17 questions.
                if i % 18 == 0 and i != 0:
                    x += 640
                    y = 10

                # Créer le text du question
                q = canvas.create_text(x, y, text=question, font=("Gulim", 11, "bold"), fill="#FFFFFF", anchor="w")
                movables.append(q)
                correct = True
                # Créer les texts des options (A B C D) avec leurs couleurs respectifs
                for j in range(len(resultats[i])):
                    n = len(resultats[i]) - j - 1
                    # S'il y a un qui est rouge, l'utilisateur a eu la question mal.
                    if resultats[i][n][1] == "#FF0000": correct = False
                    # Créer le text de l'option
                    o = canvas.create_text(600 + x - 60 * j, y, text=resultats[i][n][0], font=("Gulim", 11, "bold"),
                                           fill=resultats[i][n][1], anchor="e", justify="right")
                    movables.append(o)
                # L'indicateur qui montre si le question était correct ou non
                if correct:
                    m = canvas.create_text(620 + x, y, text="✓", font=("Gulim", 11), fill="#008000")
                else:
                    m = canvas.create_text(620 + x, y, text="X", font=("Gulim", 11, "bold"), fill="#FF0000")
                movables.append(m)
                y += 20

            canvas.create_line(0, 377, 640, 377, width=5, fill="#FFFFFF")

            # Calculer le pourcentage
            pourcentage = (points.points / len(questions)) * 100

            # Dépendant de la pourcentage, joue un son différent
            if pourcentage > 75:
                s = mixer.Sound("sons/snd_won.wav")
            else:
                s = mixer.Sound("sons/snd_youarewin.wav")
            s.set_volume(0.125)
            s.play()

            # Manipuler le bar d'HP pour montrer les questions correct
            UI.player.setMaxHP(100)
            canvas.tag_raise(UI.player.hp_txt)
            canvas.move(UI.player.hp_txt, 0, -10)
            canvas.tag_raise(UI.player.maxhp_spr.image)
            canvas.move(UI.player.maxhp_spr.image, 0, -10)
            if pourcentage > 0:
                UI.player.setHP(int(pourcentage))
                canvas.tag_raise(UI.player.hp_spr.image)
                canvas.move(UI.player.hp_spr.image, 0, -10)
                canvas.itemconfig(UI.player.hp_txt, text="{:0>2} / {:0>2}".format(points.points, len(questions)))
            else:
                UI.player.hp = 0
                canvas.itemconfig(UI.player.hp_txt, text="00 / {:0>2}".format(len(questions)))

            # Montrer le pourcentage
            canvas.create_text(414, 432, text=str(round(pourcentage, 2)) + "%", font=("MenuFont", 18), fill="#FFFFFF",
                               anchor="w", justify="left")

            # Un indicateur des pages
            global page_txt
            page_txt = canvas.create_text(10, 402, text=f"page: 1 / {int((x - 10) / 640 + 1)}", font=("MenuFont", 18),
                                          fill="#FFFFFF", anchor="w", justify="left")

            # Calculer et montrer le temps moyen
            total_t = 0
            for n in temps:
                total_t += n
            moy = round(30 - total_t / len(temps), 2)
            canvas.create_text(10, 432, text="temps moyenne: " + str(moy) + " sec", font=("MenuFont", 18),
                               fill="#FFFFFF", anchor="w", justify="left")

            # Instructions
            if (x - 10) / 640 > 0: prefix = "[Utilise ← et → pour changer de page]"
            else: prefix = ""
            canvas.create_text(320, 460, font=("Gulim", 11, "bold"), fill="#888888", anchor="center", justify="center", text=prefix + "\n[Appuyez ESC pour quitter]")

            # Pour quitter
            UI.root.bind("<Escape>", lambda e: UI.root.destroy())

        # Jouer un drumroll et montrer les résultats
        def drumRoll():
            s = mixer.Sound("sons/snd_drum.wav")
            s.set_volume(0.75)
            s.play()
            UI.root.after(2000, showResults)

        # Un sprite qui couvert l'écran
        couvert = Sprite(canvas, Image.new("RGBA", (640, 480), (0, 0, 0, 0)))
        couvert.alpha = 0

        # Faire cette sprite augmenter en opacité graduellement, pour faire un "fade out" type d'éffet
        def augmente_alpha():
            couvert.alpha += 15
            # Fade la musique aussi
            if mixer.music.get_volume() != 0: mixer.music.set_volume(mixer.music.get_volume() - 0.005)
            couvert.basespr.putalpha(couvert.alpha)
            couvert.set(couvert.basespr, replacebase=True, adjust=False)
            # Continue augmente_alpha seulement si la musique n'est pas à volume 0
            if mixer.music.get_volume() > 0:
                UI.root.after(40, augmente_alpha)
            # Lorsque la musique atteint volume 0, commence le drumRoll
            else:
                drumRoll()

        # Si on veut skipper le fade (dans un cas de game over), commence drumRoll() directement
        if not skipFade: augmente_alpha()
        else: drumRoll()

        # Une fonction qui change la page
        def changePage(dir):
            # x et y sont des variables de positionnement globales
            global x
            global y
            # Tracker quel page on est sur
            global curr_page
            # L'indicateur du page
            global page_txt

            # Calculer le montant de pages
            max_pages = (x - 10) / 640

            # Setup un son
            s = mixer.Sound("sons/menumove.wav")
            s.set_volume(0.125)

            # Avancer d'une page
            if dir == "r" and curr_page < max_pages:
                curr_page += 1
                # Bouger tous les texts 640 pixels à la gauche
                for obj in movables:
                    canvas.move(obj, -640, 0)
                # Jouer un son et changer l'indicateur
                s.play()
                canvas.itemconfig(page_txt, text=f"page: {curr_page + 1} / {int((x - 10) / 640 + 1)}")

            # Retourner d'une page
            elif dir == "l" and curr_page > 0:
                curr_page -= 1
                for obj in movables:
                    canvas.move(obj, 640, 0)
                # Jouer un son et changer l'indicateur
                s.play()
                canvas.itemconfig(page_txt, text=f"page: {curr_page + 1} / {int((x - 10) / 640 + 1)}")

    # S'il n'y avait aucune question, mettre le player sur l'autre bouton
    else:
        UI.movePlayer()


# Fonction qui crée le question
def commenceQuestion(UI):
    # Détruire le text du menu
    UI.txt.destroy()

    player = UI.player
    # La difficulté augmente après LV 5
    if player.lv >= 5:
        mode = "hard"
    else:
        mode = ""

    # Générer un expression (même méchanisme que le sommatif du deuxième unité)
    expression, expression_fancy = compileExpression(mode)

    # Calculer la réponse
    reponse = eval(expression)

    # Créer trois autres réponses, similaires à la vraie
    alt_reponses = [None] * 3
    for i in range(len(alt_reponses)):
        # Prévenir des doublons
        autres = alt_reponses.copy()
        autres.pop(i)
        while alt_reponses[i] is None or alt_reponses[i] == reponse or any(alt_reponses[i] == alt for alt in autres):
            # Si la réponse est un nombre entier, générer des options dans un intervalle de +- 5
            if reponse - floor(reponse) == 0:
                alt_reponses[i] = randrange(reponse - 5, reponse + 5)
            # Si la réponse est un décimal, générer des options dans un intervalle de +- 0.5
            else:
                # Le fonction uniform() fonctionne comme randrange() sauf pour des floats, mais il faut effectuer un
                # round() si qu'on ne veut pas un décimal long
                alt_reponses[i] = round(uniform(reponse - 0.5, reponse + 0.5), 1)

    # Ajouter la réponse à la liste
    alt_reponses.append(reponse)

    # Compiler les réponses
    options = []
    for i in range(len(alt_reponses)):
        # Sélectionner un valeur aléatoire de la liste alt_réponses
        valeur = randrange(0, len(alt_reponses))

        # Si la valeur correspond à la réponse, garde-le en note comme la valeur "correct" du question
        if alt_reponses[valeur] == reponse:
            correct = len(options) + 1

        # Ajoute la valeur à la liste d'options
        options.append(FormatNombre(alt_reponses[valeur]))

        # Enlève la valeur du liste alt_réponses (prévenir des doublons)
        alt_reponses.pop(valeur)

    # Un lambda qui crée l'objet de question pour plus tard
    createQuestion = lambda: Question(UI.root, UI.parent, player, UI.mtt, UI, f"Évalue :\n{expression_fancy}", options,
                                      correct)

    # Positionner MTT
    UI.mtt.move(2)
    UI.mtt.setAnim(UI.mtt.anim_question)

    # Positionner le player, prévenir le mouvement
    player.moveTo(player.arena.x, player.arena.y)
    player.bindInput()

    # Après un moment, créer la question
    UI.root.after(400, createQuestion)


# Les boutons, et le text
class UI:
    def __init__(self, root, parent, player, mtt):
        # Garder les arguments
        self.root = root
        self.parent = parent
        self.player = player
        self.mtt = mtt

        # Garder un référence à l'UI dans le player
        self.player.UI = self

        # Les deux boutons
        self.btnContinue = Collider(parent, Image.open("images/ui/nextbtn_0.png"), player, 320 - 80, 453,
                                    func=lambda: self.highlightBtn(self.btnContinue))
        self.btnContinue.nom = "images/ui/nextbtn_"
        self.btnQuit = Collider(parent, Image.open("images/ui/quitbtn_0.png"), player, 320 + 80, 453,
                                func=lambda: self.highlightBtn(self.btnQuit))
        self.btnQuit.nom = "images/ui/quitbtn_"

    # Montre le text
    def menuText(self, text):
        self.txt = Dialogue(self.root, self.parent, text, x=20, y=310, color="#FFFFFF", bubble=False,
                            sons=["sons/voix/uifont.wav"], takeInput=False)

    # Mettre le player sur le bouton "prochain"
    def movePlayer(self):
        self.player.moveTo(203, 454)
        self.player.bindInput(mode="buttons")

    # Fonctionnement des boutons
    def highlightBtn(self, btn):
        # Les fonctions que les boutons exécutent
        prochain_question = lambda: commenceQuestion(self)
        quitter = lambda: compileResults(self)

        # Basée sur quel bouton est sélectionné, détermine l'autre bouton et quel fonction devrait être exécuté
        if btn == self.btnContinue:
            otherBtn = self.btnQuit
            usefunc = prochain_question
        else:
            otherBtn = self.btnContinue
            usefunc = quitter

        # Changer les images des boutons
        btn.set(Image.open(btn.nom + "1.png"), adjust=False)
        otherBtn.set(Image.open(otherBtn.nom + "0.png"), adjust=False)

        # Re-enable l'autre bouton
        otherBtn.cancollide = True

        # Quand on appuie sur le clé 'z'
        def onSelect():
            # Jouer un son
            s = mixer.Sound("sons/menuconfirm.wav")
            s.set_volume(0.125)
            s.play()
            # Reset le bouton
            btn.set(Image.open(btn.nom + "0.png"), adjust=False)
            self.root.unbind("<z>")
            # usefunc
            usefunc()

        # Si on appuie 'z' sur le bouton, onSelect()
        self.root.bind("<z>", lambda a: onSelect())

        # Jouer un son
        s = mixer.Sound("sons/menumove.wav")
        s.set_volume(0.125)
        s.play()