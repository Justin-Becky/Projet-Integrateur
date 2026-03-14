from pathlib import Path

# ===================================================
# Liste d'évolution des poissons
# ===================================================
EVOLUTION_POISSON = [
    "basic_rouge", "poisson_jaune", "poisson_rayé", "green_bass", "saumon_bleu",
    "martin", "goldfish", "goldfish_long", "dore", "preuve_moyenne",
    "gros_rouge", "doris_sans_rayure", "doris_jaune", "doris_kawaii", "doris_oeil_aubernoir",
    "doris_og", "doris_bleu", "doris_brun", "doris_rouge", "doris_vert",
    "doris_rose", "hippocampe", "mouette", "crabe", "meduse",
    "puff", "poisson_mauve", "goldfish_jolie", "raie_manta", "dauphin",
    "baleine", "poisson_lion_fluo", "preuves", "preuve_complexe", "doris_shaded",
    "doris_skinny", "crevette", "anguille_cute", "poisson_chirurgien", "george_bleu",
    "beta_bleu", "Gill", "poisson_tournesol", "sunfish", "poisson_lune",
    "poisson_lune_bleu", "poisson_globe_bleu", "ton", "espadon", "espadon_croche",
    "poisson_lumiere", "poisson_lumiere2", "requin_baleine", "pokemon", "pokemon_licorne",
    "pokemon_magikarp",
]

POISSONS_TROPICAUX = [
    0, 1, 2, 3, 4, 6, 7, 8, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 26, 27, 37, 38, 39, 40, 41, 42
]

# path
BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "../Images"
PIXEL_ART_DIR = IMG_DIR / "pixel-art"

# --- Constantes de la scène ---
MARGE = 0
MOULA = 10000
# --- Multiplicateur de vitesse des animations ---
# Plus la valeur est grande, plus les animations sont lentes
FACTEUR_LENTEUR = 1

# Constante pour la largeur du market
LARGEUR_MARKET = 500
LARGEUR_INVENTAIRE = 120
