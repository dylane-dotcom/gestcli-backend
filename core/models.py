from django.db import models
from django.contrib.auth.models import AbstractUser

# ══════════════════════════════════════
# UTILISATEUR (remplace le User de Django)
# ══════════════════════════════════════
class Utilisateur(AbstractUser):
    ROLES = [
        ('admin', 'Administrateur'),
        ('medecin', 'Médecin'),
        ('secretaire', 'Secrétaire'),
        ('pharmacien', 'Pharmacien'),
        ('infirmier', 'Infirmier'),
        ('caissier', 'Caissier'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='secretaire')
    telephone = models.CharField(max_length=20, blank=True)
    specialite = models.CharField(max_length=100, blank=True)  # Pour les médecins

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

# ══════════════════════════════════════
# SERVICE MÉDICAL
# ══════════════════════════════════════
class ServiceMedical(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tarif_consultation = models.DecimalField(max_digits=10, decimal_places=2)
    salle = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

# ══════════════════════════════════════
# PATIENT
# ══════════════════════════════════════
class Patient(models.Model):
    GENRES = [('M', 'Masculin'), ('F', 'Féminin')]
    GROUPES_SANGUINS = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    genre = models.CharField(max_length=1, choices=GENRES)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPES_SANGUINS, blank=True)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    antecedents = models.TextField(blank=True)
    assurance = models.CharField(max_length=100, blank=True)
    numero_assurance = models.CharField(max_length=50, blank=True)
    medecin_traitant = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='patients'
    )
    service = models.ForeignKey(
        ServiceMedical, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    date_enregistrement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

# ══════════════════════════════════════
# DOSSIER MÉDICAL
# ══════════════════════════════════════
class DossierMedical(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier')
    date_creation = models.DateTimeField(auto_now_add=True)
    observations = models.TextField(blank=True)

    def __str__(self):
        return f"Dossier de {self.patient.nom_complet}"

# ══════════════════════════════════════
# CONSTANTES VITALES
# ══════════════════════════════════════
class ConstantesVitales(models.Model):
    dossier = models.ForeignKey(DossierMedical, on_delete=models.CASCADE, related_name='constantes')
    date_mesure = models.DateTimeField(auto_now_add=True)
    frequence_cardiaque = models.IntegerField(null=True, blank=True)
    tension_systolique = models.IntegerField(null=True, blank=True)
    tension_diastolique = models.IntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    poids = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    taille = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"Constantes {self.patient} - {self.date_mesure}"

# ══════════════════════════════════════
# RENDEZ-VOUS
# ══════════════════════════════════════
class RendezVous(models.Model):
    STATUTS = [
        ('planifie', 'Planifié'),
        ('confirme', 'Confirmé'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]
    TYPES = [
        ('consultation', 'Consultation'),
        ('suivi', 'Suivi'),
        ('urgence', 'Urgence'),
        ('chirurgie', 'Chirurgie'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendezvous')
    medecin = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='rendezvous'
    )
    service = models.ForeignKey(ServiceMedical, on_delete=models.SET_NULL, null=True)
    date_heure = models.DateTimeField()
    duree_minutes = models.IntegerField(default=30)
    type_rdv = models.CharField(max_length=20, choices=TYPES, default='consultation')
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifie')
    motif = models.TextField(blank=True)
    salle = models.CharField(max_length=50, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RDV {self.patient} - {self.date_heure}"

# ══════════════════════════════════════
# CONSULTATION
# ══════════════════════════════════════
class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    medecin = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    rendezvous = models.OneToOneField(RendezVous, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    motif = models.TextField()
    symptomes = models.TextField(blank=True)
    diagnostic = models.TextField(blank=True)
    traitement = models.TextField(blank=True)
    examens_demandes = models.TextField(blank=True)
    prochain_rdv = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Consultation {self.patient} - {self.date}"

# ══════════════════════════════════════
# MÉDICAMENT & STOCK
# ══════════════════════════════════════
class Medicament(models.Model):
    CATEGORIES = [
        ('antibiotique', 'Antibiotique'),
        ('antalgique', 'Antalgique'),
        ('anti_inflammatoire', 'Anti-inflammatoire'),
        ('antidiabetique', 'Antidiabétique'),
        ('antihypertenseur', 'Antihypertenseur'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.CharField(max_length=30, choices=CATEGORIES, default='autre')
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actuel = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=20)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    @property
    def est_critique(self):
        return self.stock_actuel <= self.seuil_alerte

# ══════════════════════════════════════
# ORDONNANCE
# ══════════════════════════════════════
class Ordonnance(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('delivree', 'Délivrée'),
    ]
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='ordonnances')
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    posologie = models.CharField(max_length=200)
    duree = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_delivrance = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.medicament.nom} - {self.posologie}"

# ══════════════════════════════════════
# FACTURE & PAIEMENT
# ══════════════════════════════════════
class Facture(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('payee', 'Payée'),
        ('impayee', 'Impayée'),
        ('annulee', 'Annulée'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='factures')
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    part_assurance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    montant_patient = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Facture #{self.id} - {self.patient.nom_complet}"

class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    prestation = models.CharField(max_length=200)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.prestation} - {self.total}"
