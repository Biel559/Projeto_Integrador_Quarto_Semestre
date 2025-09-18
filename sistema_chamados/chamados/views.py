from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import (
    UserProfile, Ambiente, Ativo, Chamado, 
    ChamadoResponsavel, ChamadoStatusHistory, Anexo
)
from .serializers import (
    UserProfileSerializer, AmbienteSerializer, AtivoSerializer,
    ChamadoSerializer, ChamadoCreateSerializer, ChamadoResponsavelSerializer,
    ChamadoStatusHistorySerializer, AnexoSerializer
)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class AmbienteViewSet(viewsets.ModelViewSet):
    queryset = Ambiente.objects.all()
    serializer_class = AmbienteSerializer

class AtivoViewSet(viewsets.ModelViewSet):
    queryset = Ativo.objects.all()
    serializer_class = AtivoSerializer
    
    @action(detail=False, methods=['get'])
    def por_ambiente(self, request):
        ambiente_id = request.query_params.get('ambiente_id')
        if ambiente_id:
            ativos = self.queryset.filter(ambiente_id=ambiente_id)
            serializer = self.get_serializer(ativos, many=True)
            return Response(serializer.data)
        return Response({'error': 'ambiente_id é obrigatório'}, status=400)

class ChamadoViewSet(viewsets.ModelViewSet):
    queryset = Chamado.objects.all().select_related('solicitante', 'ativo').prefetch_related(
        'chamadoresponsavel_set__responsavel',
        'chamadostatushistory_set__user',
        'anexo_set'
    )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChamadoCreateSerializer
        return ChamadoSerializer
    
    @action(detail=True, methods=['post'])
    def atribuir_responsavel(self, request, pk=None):
        chamado = self.get_object()
        responsavel_id = request.data.get('responsavel_id')
        role = request.data.get('role', 'responsavel_tecnico')
        
        if not responsavel_id:
            return Response({'error': 'responsavel_id é obrigatório'}, status=400)
        
        try:
            responsavel = User.objects.get(id=responsavel_id)
            chamado_responsavel, created = ChamadoResponsavel.objects.get_or_create(
                chamado=chamado,
                responsavel=responsavel,
                defaults={'role': role}
            )
            
            if created:
                # Criar histórico
                ChamadoStatusHistory.objects.create(
                    chamado=chamado,
                    user=request.user,
                    status=chamado.status,
                    descricao=f'Responsável {responsavel.username} atribuído com role {role}'
                )
                
                serializer = ChamadoResponsavelSerializer(chamado_responsavel)
                return Response(serializer.data, status=201)
            else:
                return Response({'message': 'Responsável já atribuído'}, status=200)
                
        except User.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=404)
    
    @action(detail=True, methods=['post'])
    def alterar_status(self, request, pk=None):
        chamado = self.get_object()
        novo_status = request.data.get('status')
        descricao = request.data.get('descricao', '')
        
        if novo_status not in dict(Chamado.STATUS_CHOICES):
            return Response({'error': 'Status inválido'}, status=400)
        
        status_anterior = chamado.status
        chamado.status = novo_status
        chamado.save()
        
        # Criar histórico
        ChamadoStatusHistory.objects.create(
            chamado=chamado,
            user=request.user,
            status=novo_status,
            descricao=descricao or f'Status alterado de {status_anterior} para {novo_status}'
        )
        
        serializer = self.get_serializer(chamado)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def meus_chamados(self, request):
        chamados = self.queryset.filter(solicitante=request.user)
        serializer = self.get_serializer(chamados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_status(self, request):
        status_param = request.query_params.get('status')
        if status_param:
            chamados = self.queryset.filter(status=status_param)
            serializer = self.get_serializer(chamados, many=True)
            return Response(serializer.data)
        return Response({'error': 'status é obrigatório'}, status=400)

class ChamadoStatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChamadoStatusHistory.objects.all()
    serializer_class = ChamadoStatusHistorySerializer

class AnexoViewSet(viewsets.ModelViewSet):
    queryset = Anexo.objects.all()
    serializer_class = AnexoSerializer
    
    def create(self, request, *args, **kwargs):
        chamado_id = request.data.get('chamado')
        if not chamado_id:
            return Response({'error': 'chamado é obrigatório'}, status=400)
        
        try:
            chamado = Chamado.objects.get(id=chamado_id)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(chamado=chamado)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Chamado.DoesNotExist:
            return Response({'error': 'Chamado não encontrado'}, status=404)