from django.db import models
from django.utils import timezone


class File(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_upload = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255)
    size_mb = models.FloatField()
    processed = models.BooleanField(default=False)

    def mark_processed(self):
        """Marca o arquivo como processado."""
        self.processed = True
        self.save()

    def is_processed(self) -> bool:
        """Retorna True se o arquivo estiver processado."""
        return self.processed

    def get_size_mb(self) -> float:
        """Retorna o tamanho do arquivo em MB."""
        return self.size_mb

    def rename(self, new_name: str):
        """Renomeia o arquivo."""
        self.name = new_name
        self.save()

    def __str__(self):
        return f"{self.name} ({self.size_mb:.2f} MB)"


class Certificate(models.Model):
    institution = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    date_issued = models.DateField()

    def validate_institution(self) -> bool:
        """Valida se a instituição é reconhecida (exemplo fictício)."""
        return len(self.institution.strip()) > 0

    def get_certificate_info(self) -> str:
        """Retorna uma string descritiva do certificado."""
        return f"{self.title} - {self.institution} ({self.date_issued})"

    def __str__(self):
        return f"{self.title} - {self.institution}"


class Curriculum(models.Model):
    qnt_historys = models.IntegerField(default=0)
    qnt_formations = models.IntegerField(default=0)

    def extract_historys(self):
        """Retorna uma lista de históricos (placeholder)."""
        # Aqui você pode integrar com outro model relacionado (History)
        return []

    def extract_formations(self):
        """Retorna uma lista de formações (placeholder)."""
        # Aqui você pode integrar com outro model relacionado (Formation)
        return []

    def list_histories(self):
        """Lista históricos — pode ser sobrescrito depois."""
        return self.extract_historys()

    def list_formations(self):
        """Lista formações — pode ser sobrescrito depois."""
        return self.extract_formations()

    def __str__(self):
        return f"Curriculum (Histórias: {self.qnt_historys}, Formações: {self.qnt_formations})"