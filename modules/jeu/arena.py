# --------------------------------------------------------
# Nom : William Mallette
# Titre : Arena
# Description : La boite sur l'écran, ou le 'battle arena'
# --------------------------------------------------------

# - Déclaration des fonctions ----------------------------

# Un class pour le rectangle blanc
class Arena:
    def __init__(self, root, parent):
        # Garder le fenetre
        self.root = root

        # Garder le canvas
        self.parent = parent

        # Le position du centre du rectangle
        self.x = 320
        self.y = 240

        # La grandeur du rectangle
        self.width = 100
        self.height = 100

        # Le rectangle
        self.arena = parent.create_rectangle(320-50, 240+50, 320+50, 240-50, outline="#FFFFFF", width=5)

    # Changer la grandeur du rectangle
    def resize(self, x, y):
        # Calculer les nouveaux positions des coins par rapport au centre du rectangle
        new_x1 = self.x - x/2
        new_x2 = self.x + x/2
        new_y1 = self.y + y/2
        new_y2 = self.y - y/2

        # Changer les variables
        self.width = x
        self.height = y

        # Repositionner le rectangle
        self.parent.coords(self.arena, new_x1, new_y1, new_x2, new_y2)

    # Déplacer le rectangle
    def move(self, x, y):
        self.x += x
        self.y += y
        self.parent.move(self.arena, x, y)

    # Bouger le rectangle à une position exacte
    def moveTo(self, x, y):
        # Prends les coordonnées actuels
        coords = self.parent.coords(self.arena)

        # Calculer les nouveaux coordonnées
        new_x1 = (coords[0] - self.x) + x
        new_x2 = (coords[2] - self.x) + x
        new_y1 = (coords[1] - self.y) + y
        new_y2 = (coords[3] - self.y) + y

        # Changer les variables
        self.x = x
        self.y = y

        # Repositionner le rectangle
        self.parent.coords(self.arena, new_x1, new_y1, new_x2, new_y2)