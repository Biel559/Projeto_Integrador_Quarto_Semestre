from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Ambiente(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    localizacao_ambiente = models.CharField(max_length=200, blank=True, null=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class Ativo(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('manutencao', 'Manutenção'),
        ('inativo', 'Inativo'),
    ]
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    codigo_patrimonio = models.CharField(max_length=50, unique=True, blank=True, null=True)
    qr_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.codigo_patrimonio}"

class Chamado(models.Model):
    URGENCIA_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('aguardando_responsaveis', 'Aguardando Responsáveis'),
        ('em_andamento', 'Em Andamento'),
        ('realizado', 'Realizado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    urgencia = models.CharField(max_length=20, choices=URGENCIA_CHOICES, default='media')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='aberto')
    data_sugerida = models.DateField(blank=True, null=True)
    data_abertura = models.DateTimeField(auto_now_add=True)
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chamados_solicitados')
    ativo = models.ForeignKey(Ativo, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"

class ChamadoResponsavel(models.Model):
    ROLE_CHOICES = [
        ('responsavel_tecnico', 'Responsável Técnico'),
        ('supervisor', 'Supervisor'),
    ]
    
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    data_atribuicao = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='responsavel_tecnico')

    class Meta:
        unique_together = ['chamado', 'responsavel']

    def __str__(self):
        return f"{self.chamado.titulo} - {self.responsavel.username}"

class ChamadoStatusHistory(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('aguardando_responsaveis', 'Aguardando Responsáveis'),
        ('em_andamento', 'Em Andamento'),
        ('realizado', 'Realizado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    descricao = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chamado.titulo} - {self.get_status_display()}"

class Anexo(models.Model):
    nome_arquivo = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='anexos/%Y/%m/')
    mimetype = models.CharField(max_length=100)
    tamanho_bytes = models.IntegerField()
    chamado_history = models.ForeignKey(ChamadoStatusHistory, on_delete=models.CASCADE, null=True, blank=True)
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE)
    data_upload = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.arquivo:
            self.nome_arquivo = self.arquivo.name
            self.tamanho_bytes = self.arquivo.size
            self.mimetype = getattr(self.arquivo.file, 'content_type', 'application/octet-stream')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_arquivo} - {self.chamado.titulo}"