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
    elif poisson.n == 50 or poisson.n == 51:
        x = max(limite_gauche, min(x, limite_droite))
        y = max(config.MARGE + 2 * hauteur_poisson // 3 + 3 * poisson.aquarium.height() // 5,
                min(y, poisson.aquarium.height() - 175))
    elif poisson.n in config.POISSONS_TROPICAUX:
        x = max(limite_gauche, min(x, limite_droite))
        y = max(config.MARGE + 2 * hauteur_poisson // 3,
                min(y, poisson.aquarium.height() - 175 - 1 * poisson.aquarium.height() // 5))
    else:
        # Décaler la limite gauche si le market est ouvert et décalé la limite de droite si l'inventaire est ouvert.
        x = max(limite_gauche, min(x, limite_droite))
        y = max(config.MARGE + 2 * hauteur_poisson // 3, min(y, poisson.aquarium.height() - 175))
    return x, y

# </editor-fold>

def calculer_limites(aquarium, larg, haut, poisson):
    """Retourne (gauche, droite, limite_haut, limite_bas) selon les sidebars et le type de poisson."""
    gauche = config.LARGEUR_MARKET + 50 if aquarium.proxy_market else config.MARGE
    droite = (aquarium.width() - config.LARGEUR_INVENTAIRE - larg - 25
              if aquarium.proxy_inventaire else aquarium.width() - larg - config.MARGE)

    if poisson.n == 22:
        limite_haut = config.MARGE
        limite_bas = config.MARGE

    elif poisson.n == 23:
        limite_haut = int(aquarium.height()) - 160 + 2 * haut // 3
        limite_bas = int(aquarium.height()) - 2 * haut // 3

    elif poisson.n in (50, 51):
        limite_haut = config.MARGE + 2 * haut // 3 + 3 * int(aquarium.height()) // 5
        limite_bas = int(aquarium.height()) - 175

    elif poisson.n in config.POISSONS_TROPICAUX:
        limite_haut = config.MARGE + 2 * haut // 3
        limite_bas = int(aquarium.height()) - 175 - int(aquarium.height()) // 5

    else:
        limite_haut = config.MARGE + 2 * haut // 3
        limite_bas = int(aquarium.height()) - 175

    return gauche, droite, limite_haut, limite_bas
