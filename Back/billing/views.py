from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Company, Line
from .serializers import CompanySerializer, LineSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer
    permission_classes = [IsAuthenticated]
