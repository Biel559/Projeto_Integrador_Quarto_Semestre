from django.contrib import admin
from .models import (
    UserProfile, Ambiente, Ativo, Chamado,
    ChamadoResponsavel, ChamadoStatusHistory, Anexo
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefone', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'responsavel', 'created_at']
    search_fields = ['nome', 'localizacao_ambiente']

@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_patrimonio', 'ambiente', 'status']
    list_filter = ['status', 'ambiente']
    search_fields = ['nome', 'codigo_patrimonio']

class ChamadoResponsavelInline(admin.TabularInline):
    model = ChamadoResponsavel
    extra = 1

class ChamadoStatusHistoryInline(admin.TabularInline):
    model = ChamadoStatusHistory
    extra = 0
    readonly_fields = ['created_at']

class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 0

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'solicitante', 'status', 'urgencia', 'data_abertura']
    list_filter = ['status', 'urgencia', 'data_abertura']
    search_fields = ['titulo', 'descricao']
    inlines = [ChamadoResponsavelInline, ChamadoStatusHistoryInline, AnexoInline]

@admin.register(ChamadoStatusHistory)
class ChamadoStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['chamado', 'status', 'user', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ['nome_arquivo', 'chamado', 'tamanho_bytes', 'data_upload']
    list_filter = ['mimetype', 'data_upload']