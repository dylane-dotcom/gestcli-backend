from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Utilisateur, Patient, ServiceMedical, RendezVous,
    Consultation, Medicament, Ordonnance, Facture,
    LigneFacture, DossierMedical, ConstantesVitales
)

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations GestCli', {
            'fields': ('role', 'telephone', 'specialite')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations GestCli', {
            'fields': ('role', 'telephone', 'specialite')
        }),
    )

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'genre', 'telephone', 'service', 'medecin_traitant']
    search_fields = ['nom', 'prenom', 'telephone']
    list_filter = ['genre', 'service']

@admin.register(ServiceMedical)
class ServiceMedicalAdmin(admin.ModelAdmin):
    list_display = ['nom', 'tarif_consultation', 'salle', 'actif']

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medecin', 'date_heure', 'type_rdv', 'statut']
    list_filter = ['statut', 'type_rdv']

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medecin', 'date', 'diagnostic']

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'prix_unitaire', 'stock_actuel', 'seuil_alerte']
    list_filter = ['categorie']

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'montant_total', 'statut', 'date_emission']
    list_filter = ['statut']

@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_creation']

admin.site.register(Ordonnance)
admin.site.register(LigneFacture)
admin.site.register(ConstantesVitales)