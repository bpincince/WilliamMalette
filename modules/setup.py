# --------------------------------------------------------
# Nom : William Mallette
# Titre : Setup
# Description : Installer les modules nécessaires pour le projet
# --------------------------------------------------------

# - Importation des modules ------------------------------

# Le module subprocess permet d'exécuter des commandes de shell. sys et os sont utilisés pour trouver l'interpreteur
from subprocess import call
from sys import executable
from os import path

# - Variables globales -----------------------------------

# Trouver le dossier de l'interpreteur
dossier = path.dirname(executable)

# - Déclaration des fonctions ----------------------------

# Assurer que l'utilisateur a contrôle de l'installation
def confirmation(reponse):
    if reponse.lower() == "y":
        print("D'accord!")
        return True
    else:
        print("Ce module est nécessaire pour le fonctionnement du jeu.\nEssayez encore.")
        return False

# Effectue les opérations nécessaires pour établir les modules du projet
def setup():
    # Pillow est un module puissant qui gère des images.
    try:
        import PIL
    except:
        # J'ai modifié les installations pour demander une confirmation de l'utilisateur
        reponse = input("Installez Pillow? (Y/N)\n")
        if confirmation(reponse): call(f"py -m pip install --target={dossier} pillow")
        else: setup()

    # Pygame a beaucoup d'utilités, y inclus un contrôleur d'audio efficace et flexible.
    try:
        import pygame
    except:
        reponse = input("Installez Pygame? (Y/N)\n")
        if confirmation(reponse): call(f"py -m pip install --target={dossier} pygame")
        else: setup()

    # Un nouveau module pour moi, Pyglet. Utile pour des fichiers média (dans mon cas, les fonts)
    try:
        import pyglet
    except:
        reponse = input("Installez Pyglet? (Y/N)\n")
        if confirmation(reponse): call(f"py -m pip install --target={dossier} pyglet")
        else: setup()