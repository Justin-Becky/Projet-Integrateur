import config

# <editor-fold desc="Clamping dynamique">
# --- Garde une position dans les limites de la scène ---
def clamper_position(x, y, largeur_poisson, hauteur_poisson, poisson):
    limite_gauche = config.LARGEUR_MARKET + 50 if poisson.aquarium and poisson.aquarium.proxy_market else config.MARGE
    limite_droite = poisson.aquarium.width() - config.LARGEUR_INVENTAIRE - largeur_poisson - 25 if (
            poisson.aquarium and poisson.aquarium.proxy_inventaire) else (
            poisson.aquarium.width() - largeur_poisson - config.MARGE)
    if poisson.n == 22:
        x = max(limite_gauche, min(x, limite_droite))
        y = config.MARGE
    elif poisson.n == 23:
        x = max(limite_gauche, min(x, limite_droite))
        y = max(int(poisson.aquarium.height()) - 160 + 2 * hauteur_poisson // 3, min(
            y, poisson.aquarium.height() - 2 * hauteur_poisson // 3))
    else:
        # Décaler la limite gauche si le market est ouvert et décalé la limite de droite si l'inventaire est ouvert.
        x = max(limite_gauche, min(x, limite_droite))
        y = max(config.MARGE + 2 * hauteur_poisson // 3, min(y, poisson.aquarium.height() - 175))
    return x, y

# </editor-fold>
