# --------------------------------------------------------
# Nom : William Mallette
# Titre : Dialogue
# Description : Émuler les objets de text d'Undertale
# --------------------------------------------------------

# - Importation des modules ------------------------------

from tkinter import *
from pygame import mixer
from random import randrange

# - Variables globales -----------------------------------

# Liste de marqueurs de ponctuation
punctuation = [",", ".", ":", ";", "!", "?"]

# - Déclaration des fonctions ----------------------------

# Class pour le dialogue
class Dialogue:
    def __init__(self, root, parent, text, x=320, y=240, color="#000000", bubble=True, sons=None, side="r", takeInput=True, endfunc=None):
        # Convertir des strings seuls en liste contenant ce string, pour bien fonctionner avec des one-liners
        if str(type(text)) == "<class 'str'>": text = [text]

        # Garder le fonction à exécuter au fin
        self.onEnd = endfunc

        # Garder la liste de text et un index
        self.lines = text
        self.line_index = 0

        # Une liste des sons
        self.sons = sons

        # Garder le fenêtre
        self.root = root

        # Garder le canvas
        self.parent = parent

        # Le bulle
        if bubble:
            self.bspr = PhotoImage(file=f"images/bulles/{side}.png")
            if side == "r": anchor = "w"
            else: anchor = "e"
            self.bulle = parent.create_image(x, y, image=self.bspr, anchor=anchor)
            font = ("Gulim", 11, "bold")

        # S'il n'y a pas de bulle, utilise Determination Mono
        else:
            font = ("Determination Mono", 20)
            # Il faut encore créer quelque chose pour être détruit plus tard
            self.bulle = parent.create_image(x, y)

        # Créer l'objet de text, j'aimerais utiliser le propriété 'width', mais ce n'est pas possible avec notre méthode
        if side == "r": x_offset = 32
        else: x_offset = -230
        self.textobj = parent.create_text(x + x_offset, y - 40, fill=color, font=font, anchor="nw")

        # Bind les clés si takeInput est True
        if takeInput:
            # Bind le clé 'z' au fonction d'avance
            root.bind("<z>", lambda a: self.tryProgress())
            # Bind le clé 'x' au fonction de skip
            root.bind("<x>", lambda a: self.showText())

        # Initier le premier ligne de text
        self.prepStr(text[0])

    # Format le text correctement, et commence à taper
    def prepStr(self, text):
        # Reset l'objet de text
        self.parent.itemconfig(self.textobj, text="")

        # Garder le string entier
        self.fulltxt = text

        # Une liste pour les caractères du texte
        self.characters = []

        # Un index du caractère
        self.curr_char = 0

        # Remplir la liste
        for char in text:
            self.characters.append(char)

        # Commence printText
        self.root.after(10, self.printText)

    # Créer un effet "typewriter" pour le texte
    def printText(self):
        # Obtenir le texte déjà montré
        curr_text = self.parent.itemcget(self.textobj, 'text')
        delay = 0

        # Faire certain qu'on ne dépasse pas la limite de la liste
        if self.curr_char < len(self.characters):
            # Si la prochaine caractère à montrer est du ponctuation
            if any(self.characters[self.curr_char] == punc for punc in punctuation):
                # Encore, prévenir des erreurs "out of range"
                if self.curr_char + 1 < len(self.characters):
                    # Vérifier si le prochain caractère n'est pas du ponctuation
                    # Sinon, attendre plus longtemps avant de s'avancer
                    # Ceci permet des pauses comme "..." ou "!!!" sans créer un grand pause
                    if not any(self.characters[self.curr_char+1] == punc for punc in punctuation):
                        delay = 300

            # Si ce n'est pas du ponctuation, avance normalement
            else: delay = 30

            # Ajoute la nouveau caractère
            self.parent.itemconfig(self.textobj, text=curr_text + self.characters[self.curr_char])

            # Augmente l'index
            self.curr_char += 1

            # Jouer un des sons à chaque caractère alternatif
            if self.sons and self.curr_char%2 == 1:
                s = mixer.Sound(self.sons[randrange(0, len(self.sons))])
                s.set_volume(0.125)
                s.play()

            # Attendre, et recommence
            self.root.after(delay, self.printText)

    # Montre l'entier du texte
    def showText(self):
        # Arrête printText en changant self.curr_char
        self.curr_char = len(self.fulltxt)

        # Montre l'entier du texte
        self.parent.itemconfig(self.textobj, text=self.fulltxt)

    # Essaye d'avancer le text
    def tryProgress(self):
        # Vérifie que le text est fini
        if self.parent.itemcget(self.textobj, "text") == self.fulltxt:
            # Si on n'est pas au fin de la liste, avance au prochain ligne
            if self.line_index < len(self.lines) - 1:
                self.line_index += 1
                self.prepStr(self.lines[self.line_index])
            # Si le text est terminé, détruit l'objet
            else:
                self.destroy()

    # Enlever l'objet de l'écran, exécute le fonction gardé dans self.onEnd
    def destroy(self):
        # Arrêter le progression du text s'il est encore en train de taper
        self.showText()
        # Détruire les objets
        self.parent.delete(self.textobj)
        self.parent.delete(self.bulle)
        # Enlève les binds
        self.root.unbind("<z>")
        self.root.unbind("<x>")
        # self.onEnd
        if self.onEnd: self.onEnd()