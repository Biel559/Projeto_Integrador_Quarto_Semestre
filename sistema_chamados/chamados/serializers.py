from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Ambiente, Ativo, Chamado, 
    ChamadoResponsavel, ChamadoStatusHistory, Anexo
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'telefone', 'endereco', 'created_at', 'updated_at']

class AmbienteSerializer(serializers.ModelSerializer):
    responsavel = UserSerializer(read_only=True)
    
    class Meta:
        model = Ambiente
        fields = '__all__'

class AtivoSerializer(serializers.ModelSerializer):
    ambiente = AmbienteSerializer(read_only=True)
    
    class Meta:
        model = Ativo
        fields = '__all__'

class ChamadoResponsavelSerializer(serializers.ModelSerializer):
    responsavel = UserSerializer(read_only=True)
    
    class Meta:
        model = ChamadoResponsavel
        fields = '__all__'

class ChamadoStatusHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChamadoStatusHistory
        fields = '__all__'

class AnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexo
        fields = '__all__'

class ChamadoSerializer(serializers.ModelSerializer):
    solicitante = UserSerializer(read_only=True)
    ativo = AtivoSerializer(read_only=True)
    responsaveis = ChamadoResponsavelSerializer(many=True, read_only=True)
    historico = ChamadoStatusHistorySerializer(many=True, read_only=True, source='chamadostatushistory_set')
    anexos = AnexoSerializer(many=True, read_only=True, source='anexo_set')
    
    class Meta:
        model = Chamado
        fields = '__all__'

class ChamadoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chamado
        fields = ['titulo', 'descricao', 'urgencia', 'data_sugerida', 'ativo']
        
    def create(self, validated_data):
        validated_data['solicitante'] = self.context['request'].user
        return super().create(validated_data)