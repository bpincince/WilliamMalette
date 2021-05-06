# --------------------------------------------------------
# Nom : William Mallette
# Titre : Tuteur mathématique
# Description : Présente une expression mathématique qui doit être évalué par l'usager
# --------------------------------------------------------

# - Importation des modules ------------------------------
import random

# - Variables globales -----------------------------------
operateurs = ["+", "-", "*", "/", "**"]
exposants = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"]
questions = []
resultats = []
temps = []

# - Déclaration des fonctions ----------------------------

def RandOperator():
    # Retourner un élément aléatoire de la liste d'opérateurs
    return operateurs[random.randrange(0, len(operateurs))]

def NombresCompatibles(op):
    # Choisir un nombre de départ
    n1 = random.randrange(-12, 12)
    n2 = 1
    # Générer un deuxième nombre qui est compatible avec nos paramètres
    if op == "**":
        # Limite un exposant à un nombre entier entre 0 et 9 avec un résultat entre -150 et 150
        temp_n2 = 151
        while (not -150 < ((n1) ** temp_n2) < 150) or temp_n2 == 151:
            temp_n2 = random.randrange(0, 9)
        n2 = temp_n2
    elif op == "/":
        # Limiter les résultats à des nombres entiers, des demi-entiers, ou des divisions par 10
        decimal = 1
        while not (decimal == 0 or decimal == 5 or n2 == 10):
            temp_n2 = random.randrange(-12,12)
            # Éviter les divisions par 0
            if temp_n2 != 0:
                n2 = temp_n2
                decimal = round(((n1 / n2) % 1) * 10, 1)
    else:
        # Pour les autres opérateurs, c'est correct d'utiliser la même méthode qu'avec n1
        n2 = random.randrange(-12,12)
    return n1, n2

def FormatNombre(n):
    # J'ai découvert un anomalie ou il y avait des nombres entiers en forme de float qui apparaient comme "(-1.0)" par
    # exemple. Ce n'était pas un problème quand l'utilisateur fallait entrer leur réponse, mais avec les choix ce
    # problème dévoilait la réponse. Alors, j'ai ajouté ce parti à cette fonction.
    if str(n).find(".") > -1:
        if str(n)[str(n).find("."):len(str(n))] == ".0":
            _n = int(n)
        else:
            _n = n
    else:
        _n = n

    # Mettre les nombres négatifs dans les parenthèses, transformer le nombre en string
    if float(n) < 0:
        return "({})".format(_n)
    else:
        return "{}".format(_n)

def StyliseExpression(exp):
    # Entièrement asthétique. Note que c'est encore nécessaire de garder l'expression initiale puisque eval() ne peut pas utiliser les caractères spéciales.
    # Remplace les exposants "x ** n" avec une caractère spéciale: "xⁿ".
    nstr = exp
    exposant_pos = exp.find(" ** ")
    if exposant_pos > 0:
        # Extraire le nombre de l'exposant, remplacer " ** n" avec "ⁿ"
        exposant_n = int(exp[exposant_pos+4])
        vielle_exp = " ** {}".format(exposant_n)
        nstr = exp.replace(vielle_exp, exposants[exposant_n])
    return nstr

def RandomExpression():
    # Utilise les fonctions ci-dessus pour compiler une expression mathématique
    operation = RandOperator()
    n1, n2 = NombresCompatibles(operation)
    expression = "{} {} {}".format(FormatNombre(n1), operation, FormatNombre(n2))
    expression_fancy = StyliseExpression(expression)
    return expression, expression_fancy

# Ce qui reste du fonction "Tuteur"
def compileExpression(mode=""):
    if mode == "hard":
        # Hardmode additionne deux expressions ensembles.
        exp1, expf1 = RandomExpression()
        exp2, expf2 = RandomExpression()
        expression = "({}) + ({})".format(exp1, exp2)
        expression_fancy = "({}) + ({})".format(expf1, expf2)
    else:
        expression, expression_fancy = RandomExpression()
    return expression, expression_fancy