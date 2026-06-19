from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'rendezvous', views.RendezVousViewSet)
router.register(r'consultations', views.ConsultationViewSet)
router.register(r'medicaments', views.MedicamentViewSet)
router.register(r'ordonnances', views.OrdonnanceViewSet)
router.register(r'factures', views.FactureViewSet)
router.register(r'services', views.ServiceMedicalViewSet)
router.register(r'personnel', views.PersonnelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/me/', views.me_view, name='me'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('patients/<int:patient_id>/dossier/', views.dossier_patient, name='dossier-patient'),
    path('ordonnances/<int:ordonnance_id>/delivrer/', views.delivrer_ordonnance, name='delivrer-ordonnance'),
]