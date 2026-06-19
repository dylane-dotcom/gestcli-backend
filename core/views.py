from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import (
    Utilisateur, Patient, ServiceMedical, RendezVous,
    Consultation, Medicament, Facture, DossierMedical, Ordonnance
)
from .serializers import (
    UtilisateurSerializer, PatientSerializer, ServiceMedicalSerializer,
    RendezVousSerializer, ConsultationSerializer, MedicamentSerializer,
    FactureSerializer, DossierMedicalSerializer, RegisterSerializer,
    OrdonnanceSerializer
)

# ══════════════════════════════════════
# AUTHENTIFICATION
# ══════════════════════════════════════
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'nom': user.get_full_name(),
                'role': user.role,
                'email': user.email,
                'specialite': user.specialite,
            }
        })
    return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Utilisateur créé avec succès'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UtilisateurSerializer(request.user)
    return Response(serializer.data)

# ══════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    from datetime import date
    aujourd_hui = date.today()
    stats = {
        'total_patients': Patient.objects.count(),
        'rdv_aujourd_hui': RendezVous.objects.filter(date_heure__date=aujourd_hui).count(),
        'rdv_confirmes': RendezVous.objects.filter(date_heure__date=aujourd_hui, statut='confirme').count(),
        'urgences': RendezVous.objects.filter(date_heure__date=aujourd_hui, type_rdv='urgence').count(),
        'medicaments_critiques': Medicament.objects.filter(stock_actuel__lte=20).count(),
        'factures_impayees': Facture.objects.filter(statut='impayee').count(),
        'personnel_total': Utilisateur.objects.filter(is_active=True).count(),
        'ordonnances_attente': Ordonnance.objects.filter(statut='en_attente').count(),
    }
    return Response(stats)

# ══════════════════════════════════════
# PATIENTS
# ══════════════════════════════════════
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-date_enregistrement')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Patient.objects.all()
        search = self.request.query_params.get('search')
        service = self.request.query_params.get('service')
        if search:
            queryset = queryset.filter(nom__icontains=search) | queryset.filter(prenom__icontains=search)
        if service:
            queryset = queryset.filter(service__nom=service)
        return queryset.order_by('-date_enregistrement')

# ══════════════════════════════════════
# RENDEZ-VOUS
# ══════════════════════════════════════
class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all().order_by('date_heure')
    serializer_class = RendezVousSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RendezVous.objects.all()
        date = self.request.query_params.get('date')
        medecin = self.request.query_params.get('medecin')
        if date:
            queryset = queryset.filter(date_heure__date=date)
        if medecin:
            queryset = queryset.filter(medecin__id=medecin)
        return queryset.order_by('date_heure')

# ══════════════════════════════════════
# CONSULTATIONS
# ══════════════════════════════════════
class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all().order_by('-date')
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        consultation = serializer.save()
        DossierMedical.objects.get_or_create(patient=consultation.patient)

# ══════════════════════════════════════
# DOSSIER MÉDICAL
# ══════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dossier_patient(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        dossier, created = DossierMedical.objects.get_or_create(patient=patient)
        serializer = DossierMedicalSerializer(dossier)
        consultations = Consultation.objects.filter(patient__id=patient_id).order_by('-date')
        consult_serializer = ConsultationSerializer(consultations, many=True)
        return Response({
            'dossier': serializer.data,
            'consultations': consult_serializer.data,
        })
    except Patient.DoesNotExist:
        return Response({'error': 'Patient non trouvé'}, status=status.HTTP_404_NOT_FOUND)

# ══════════════════════════════════════
# MÉDICAMENTS
# ══════════════════════════════════════
class MedicamentViewSet(viewsets.ModelViewSet):
    queryset = Medicament.objects.all().order_by('nom')
    serializer_class = MedicamentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Medicament.objects.all()
        critique = self.request.query_params.get('critique')
        if critique == 'true':
            queryset = queryset.filter(stock_actuel__lte=20)
        return queryset.order_by('nom')

# ══════════════════════════════════════
# ORDONNANCES
# ══════════════════════════════════════
class OrdonnanceViewSet(viewsets.ModelViewSet):
    queryset = Ordonnance.objects.all().order_by('-date_creation')
    serializer_class = OrdonnanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ordonnance.objects.all()
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset.order_by('-date_creation')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delivrer_ordonnance(request, ordonnance_id):
    try:
        ordonnance = Ordonnance.objects.get(id=ordonnance_id)
        medicament = ordonnance.medicament

        if medicament.stock_actuel <= 0:
            return Response(
                {'error': 'Stock insuffisant pour ce médicament'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Décrémente le stock et marque comme délivrée
        medicament.stock_actuel -= 1
        medicament.save()

        ordonnance.statut = 'delivree'
        ordonnance.date_delivrance = timezone.now()
        ordonnance.save()

        serializer = OrdonnanceSerializer(ordonnance)
        return Response(serializer.data)
    except Ordonnance.DoesNotExist:
        return Response({'error': 'Ordonnance non trouvée'}, status=status.HTTP_404_NOT_FOUND)

# ══════════════════════════════════════
# FACTURES
# ══════════════════════════════════════
class FactureViewSet(viewsets.ModelViewSet):
    queryset = Facture.objects.all().order_by('-date_emission')
    serializer_class = FactureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Facture.objects.all()
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset.order_by('-date_emission')

# ══════════════════════════════════════
# SERVICES MÉDICAUX
# ══════════════════════════════════════
class ServiceMedicalViewSet(viewsets.ModelViewSet):
    queryset = ServiceMedical.objects.filter(actif=True)
    serializer_class = ServiceMedicalSerializer
    permission_classes = [IsAuthenticated]

# ══════════════════════════════════════
# PERSONNEL
# ══════════════════════════════════════
class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.filter(is_active=True)
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Utilisateur.objects.filter(is_active=True)
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset