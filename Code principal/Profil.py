
"""
class Profil:
    def __init__(self):
        super().__init__()
        self.dialogue_information = None
        self.barre_statut = None
        self.dialogue_deconnexion = None
        self.dataframe = pd.read_csv("donneesutilisateurs", delimiter=",")
        self.est_connecter = False
        self.dialogue = None
        self.bouton_creer = None
        self.bouton_connecter = None
        self.mot_passe = None
        self.utilisateur = QLineEdit()

    def debut(self):
        self.dialogue = QDialog()
        self.dialogue.setWindowIcon(QPixmap("images/icone.png"))
        self.dialogue.setWindowTitle("Connexion")
        disposition_connexion = QVBoxLayout()

        # Le libellé pour Connexion Profil
        libelle_profil = QLabel("Connexion Profil")
        libelle_profil.setFont(QFont("Bauhaus 93", 15))
        disposition_connexion.addWidget(libelle_profil)

        # Le nom d'utilisateur
        libelle_utilisateur = QLabel("Nom d'utilisateur")
        self.utilisateur = QLineEdit()
        disposition_utilisateur = QHBoxLayout()
        disposition_utilisateur.addWidget(libelle_utilisateur)
        disposition_utilisateur.addWidget(self.utilisateur)
        disposition_connexion.addLayout(disposition_utilisateur)

        # Le QLabel et le QLineEdit pour le mot de passe
        libelle_mot_passe = QLabel("Mot de passe")
        self.mot_passe = QLineEdit()
        self.mot_passe.setEchoMode(QLineEdit.EchoMode.Password)
        disposition_mot_passe = QHBoxLayout()
        disposition_mot_passe.addWidget(libelle_mot_passe)
        disposition_mot_passe.addWidget(self.mot_passe)
        disposition_connexion.addLayout(disposition_mot_passe)

        # Barre statut qui indique s'il y a une erreur dans les entrées de l'utilisateur.
        self.barre_statut = QStatusBar()
        self.barre_statut.setSizeGripEnabled(False)
        self.barre_statut.setFont(QFont("Bauhaus 93", 9))
        self.barre_statut.setStyleSheet("color: rgb(255, 0, 0);")
        disposition_connexion.addWidget(self.barre_statut)

        # Bouton Connecter et Créer
        self.bouton_connecter = QRadioButton("Se connecter à son profil")
        self.bouton_creer = QRadioButton("Se créer un compte")
        self.bouton_creer.setChecked(True)    # Par défault le bouton créer est coché.
        disposition_connexion.addWidget(self.bouton_connecter)
        disposition_connexion.addWidget(self.bouton_creer)

        # Bouton Annuler, pour fermer la fenêtre et ne pas se créer de compte
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.dialogue.close)
        disposition_connexion.addWidget(bouton_annuler)
        # Bouton Ok permet de vérifier les saisies de l'utilisateur.
        bouton_ok = QPushButton("Ok")
        bouton_ok.clicked.connect(self.verification)
        disposition_connexion.addWidget(bouton_ok)

        self.dialogue.setLayout(disposition_connexion)
        self.dialogue.exec()

    def verification(self):
        if (self.utilisateur.text().count(",") == 0 and self.utilisateur.text().count(" ") == 0
                and self.utilisateur.text() != ""):
            if (self.mot_passe.text().count(",") == 0 and self.mot_passe.text().count(" ") == 0
                    and self.utilisateur.text() != ""):
                # Lorsque les conditions sont respectées créations ou connection au compte.
                if self.bouton_creer.isChecked():
                    self.se_creer()
                else:
                    self.se_connecter()
            else:
                self.barre_statut.showMessage("L'espace et la virgule ne sont pas permis", timeout=5000)
        else:
            self.barre_statut.showMessage("L'espace et la virgule ne sont pas permis", timeout=5000)

    def se_connecter(self):
        self.dataframe = pd.read_csv("donneesutilisateurs", delimiter=",")
        # S'assure que le nom d'utilisateur se retrouve dans la série NOM_UTILISATEUR.
        if self.utilisateur.text() in self.dataframe["NOM_UTILISATEUR"].values:
            # Puisque le nom d'utilisateur qu'on recherche n'est présent qu'une seule fois dans la série
            # NOM_UTILISATEUR (voir la méthode se_créer()), alors on sait qu'il n'y aura qu'un seul mot de passe
            # retourné.
            for mot_de_passe in self.dataframe[self.dataframe["NOM_UTILISATEUR"]
                                               == self.utilisateur.text()]["MOT_DE_PASSE"]:
                if self.mot_passe.text() == mot_de_passe:
                    # L'attribut est_connecter permet l'exécution de la méthode modifier_information()
                    self.est_connecter = True
                    self.dialogue.close()
                # Message d'erreur si le mot de passe ne correspond pas à celui enregistrer.
                else:
                    self.barre_statut.showMessage("Le mot de passe n'est pas valide", timeout=5000)
        # Message d'erreur si le nom d'utilisateur n'est pas dans la série NOM_UTILISATEUR.
        else:
            self.barre_statut.showMessage("Le nom d'utilisateur n'est pas valide", timeout=5000)

    def se_creer(self):
        self.dataframe = pd.read_csv("donneesutilisateurs", delimiter=",")
        # Si le nom d'utilisateur est déjà utilisé, message d'erreur.
        if self.utilisateur.text() in self.dataframe["NOM_UTILISATEUR"].values:
            self.barre_statut.showMessage("Le nom utilisateur est déjà utilisé",
                                          timeout=5000)
        # Sinon, le compte est créé.
        else:
            with open("donneesutilisateurs", "a", encoding="utf-8") as fichier:
                fichier.write(f"{self.utilisateur.text()},{self.mot_passe.text()}, \n")
            self.est_connecter = True
            self.dialogue.close()

    def information(self):
        nb_parties = "0"
        score_moyen = "indéterminé"
        hi_score = "indéterminé"
        self.dialogue_information = QMessageBox()
        self.dialogue_information.setWindowIcon(QIcon("images/icone.png"))
        # Le nom d'utilisateur étant unique, il n'y aura qu'une seule chaine de caractères SCORES retournée.
        for scores in self.dataframe[self.dataframe["NOM_UTILISATEUR"]
                                     == self.utilisateur.text()]["SCORES"]:
            if scores is not None or " ":
                # Enlève les espaces de chaque côté, puis transforme la chaine de caractères en liste.
                scores = scores.strip()
                scores = scores.split(" ")
                nb_parties = len(scores)
                score_moyen = sum(map(float, scores))/nb_parties
                hi_score = max(map(float, scores))
            else:
                nb_parties = "0"
                score_moyen = "indéterminé"
                hi_score = "indéterminé"
        self.dialogue_information.about(QMainWindow(), "Information Profil", f" Votre nom d'utilisateur :"
                                                                             f" {self.utilisateur.text()} \n Nombres "
                                                                             f"de parties jouées : {nb_parties}\n "
                                                                             f"Votre score moyen : {score_moyen} \n "
                                                                             f"Votre score le plus élevé : {hi_score}")

    def fin(self):
        self.dialogue_deconnexion = QDialog()
        self.dialogue.setWindowIcon(QPixmap("images/icone.png"))
        self.dialogue_deconnexion.setWindowTitle("Déconnexion")
        disposition_deconnexion = QVBoxLayout()

        # Libellée Déconnexion Profil
        libelle_profil = QLabel("Déconnexion Profil")
        libelle_profil.setFont(QFont("Bauhaus 93", 15))
        disposition_deconnexion.addWidget(libelle_profil)

        # Libellé phrase déconnexion
        libelle_deconnexion = QLabel(f"Voulez-vous vous déconnecter de votre compte {self.utilisateur.text()} ?")
        disposition_deconnexion.addWidget(libelle_deconnexion)

        disposition_bouton = QHBoxLayout()
        # Bouton oui, permet de se déconnecter.
        bouton_oui = QPushButton("Oui")
        bouton_oui.clicked.connect(self.se_deconnecter)
        disposition_bouton.addWidget(bouton_oui)
        # Bouton annuler, permet de fermer la fenêtre sans se déconnecter.
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.dialogue_deconnexion.close)
        disposition_bouton.addWidget(bouton_annuler)

        disposition_deconnexion.addLayout(disposition_bouton)
        self.dialogue_deconnexion.setLayout(disposition_deconnexion)
        self.dialogue_deconnexion.exec()

    def se_deconnecter(self):
        self.est_connecter = False
        self.dialogue_deconnexion.close()

    def modifier_information(self, dernier_score):
        # Seulement si l'attribut est_connecter est vrai que le dernier score est ajouté.
        if self.est_connecter:
            # Permet d'ajouter le dernier score aux anciens scores de l'utilisateur qui était actuellement connecté.
            with open("donneesutilisateurs", mode="r", encoding="utf-8") as fichier:
                reader = csv.DictReader(fichier, delimiter=",")
                lignes = []
                for ligne in reader:
                    if ligne["NOM_UTILISATEUR"] == self.utilisateur.text():
                        ligne["SCORES"] += f"{str(dernier_score)} "
                    # Ajoute les lignes à la liste de lignes qui vont être réécrites
                    lignes.append(ligne)
            with open("donneesutilisateurs", mode="w", newline="", encoding="utf-8") as fichier:
                writter = csv.DictWriter(f=fichier, fieldnames=["NOM_UTILISATEUR",
                                                                "MOT_DE_PASSE", "SCORES"])
                writter.writeheader()
                writter.writerows(lignes)
"""
