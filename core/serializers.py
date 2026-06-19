from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    Utilisateur, Patient, ServiceMedical, RendezVous,
    Consultation, Medicament, Ordonnance, Facture,
    LigneFacture, DossierMedical, ConstantesVitales
)

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'telephone', 'specialite']

class ServiceMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMedical
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    medecin_traitant_nom = serializers.SerializerMethodField()
    service_nom = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'

    def get_medecin_traitant_nom(self, obj):
        if obj.medecin_traitant:
            return obj.medecin_traitant.get_full_name()
        return None

    def get_service_nom(self, obj):
        if obj.service:
            return obj.service.nom
        return None

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        born = obj.date_naissance
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return age

    def get_nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"

class ConstantesVitalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstantesVitales
        fields = '__all__'

class DossierMedicalSerializer(serializers.ModelSerializer):
    constantes = ConstantesVitalesSerializer(many=True, read_only=True)
    patient_nom = serializers.SerializerMethodField()

    class Meta:
        model = DossierMedical
        fields = '__all__'

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

class RendezVousSerializer(serializers.ModelSerializer):
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()
    service_nom = serializers.SerializerMethodField()

    class Meta:
        model = RendezVous
        fields = '__all__'

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

    def get_medecin_nom(self, obj):
        return obj.medecin.get_full_name()

    def get_service_nom(self, obj):
        return obj.service.nom if obj.service else None

class ConsultationSerializer(serializers.ModelSerializer):
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = '__all__'

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

    def get_medecin_nom(self, obj):
        return obj.medecin.get_full_name()

class MedicamentSerializer(serializers.ModelSerializer):
    est_critique = serializers.ReadOnlyField()
    niveau_stock = serializers.SerializerMethodField()

    class Meta:
        model = Medicament
        fields = '__all__'

    def get_niveau_stock(self, obj):
        if obj.stock_actuel <= obj.seuil_alerte * 0.3:
            return 'Critique'
        elif obj.stock_actuel <= obj.seuil_alerte:
            return 'Faible'
        return 'Bon'

class OrdonnanceSerializer(serializers.ModelSerializer):
    medicament_nom = serializers.SerializerMethodField()
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()
    prix_unitaire = serializers.SerializerMethodField()

    class Meta:
        model = Ordonnance
        fields = '__all__'

    def get_medicament_nom(self, obj):
        return obj.medicament.nom

    def get_patient_nom(self, obj):
        return obj.consultation.patient.nom_complet

    def get_medecin_nom(self, obj):
        return obj.consultation.medecin.get_full_name()

    def get_prix_unitaire(self, obj):
        return obj.medicament.prix_unitaire

class LigneFactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneFacture
        fields = '__all__'

class FactureSerializer(serializers.ModelSerializer):
    lignes = LigneFactureSerializer(many=True, read_only=True)
    patient_nom = serializers.SerializerMethodField()

    class Meta:
        model = Facture
        fields = '__all__'

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Utilisateur
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'role', 'telephone', 'specialite']

    def create(self, validated_data):
        user = Utilisateur.objects.create_user(**validated_data)
        return user