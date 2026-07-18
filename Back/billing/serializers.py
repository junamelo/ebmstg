from rest_framework import serializers
from .models import Company, Line, CategorieClient, CycleFacturation

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'compte', 'raison_sociale', 'code_commercial', 'nom_commercial', 
                  'categorie', 'adresse', 'adresse2', 'statut', 'payeur', 'date_creation', 'date_modification']
        read_only_fields = ['id', 'date_creation', 'date_modification']

class LineSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    
    class Meta:
        model = Line
        fields = ['id', 'company', 'company_name', 'msisdn', 'utilisateur', 'forfait', 
                  'cycle', 'option_blackberry', 'option_nolimit', 'est_incognito', 
                  'facture_detaillee', 'est_non_revenu', 'statut', 'employe', 
                  'date_creation', 'date_modification']
        read_only_fields = ['id', 'date_creation', 'date_modification']
