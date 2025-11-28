from django.db import models
from django.utils import timezone
import os

from rh.pdf_extractor import PDFExtractor

# Common
from common.embedding import create_embedding

class File(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_upload = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=255)
    size_mb = models.FloatField()
    processed = models.BooleanField(default=False)

    full_text = models.TextField(null=True, blank=True)

    # word_cloud AGORA vai guardar as entities extraídas
    word_cloud = models.JSONField(blank=True, null=True)

    # vetor de embedding (lista de floats)
    embedding = models.JSONField(null=True, blank=True)

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

    def process_file(self, file_path: str) -> dict:
        """
        Processa o arquivo PDF e extrai:
        - full_text
        - entities (word_cloud)
        - embedding
        """

        extractor = PDFExtractor(file_path)

        data = {
            "path": file_path,
            "extension": os.path.splitext(file_path)[1],
            "processed_at": timezone.now().isoformat(),
            "pdf_with_text": extractor.pdf_with_text(),
        }

        if data["pdf_with_text"]:
            # Informações gerais (currículo)
            info = extractor.extract_resume_info()
            data["info"] = info

            # Entities
            entities = extractor.extract_entities()
            data["entities"] = entities

            # Salvamos entities como word_cloud
            self.word_cloud = entities

            # Texto completo
            self.full_text = extractor.text

            # Embedding a partir do texto completo
            self.embedding = create_embedding(self.full_text)

            # marca como processado
            self.processed = True
            self.save()

        return data


class Certificate(File):
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


class Curriculum(File):
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

class History(models.Model):
    """
    Experiências profissionais do currículo.
    """
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='histories')
    company = models.CharField(max_length=255)
    describe = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    calculated_experience_time_months = models.PositiveIntegerField(default=0)

    def calculate_experience_time(self):
        """Calcula duração em meses."""
        end = self.end_date or timezone.now().date()
        return (end.year - self.start_date.year) * 12 + (end.month - self.start_date.month)

    def is_current_job(self):
        return self.end_date is None

    def get_summary(self):
        return f"{self.company} ({self.start_date:%Y} - {self.end_date:%Y if self.end_date else 'atual'})"

    def save(self, *args, **kwargs):
        self.calculated_experience_time_months = self.calculate_experience_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company} - {self.describe[:40] if self.describe else ''}"


class Formation(models.Model):
    """
    Formação acadêmica ou técnica do currículo.
    """
    curriculum = models.ForeignKey(Curriculum, on_delete=models.CASCADE, related_name='formations')
    level = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def is_completed(self):
        return self.end_date is not None

    def get_duration_years(self):
        end = self.end_date or timezone.now().date()
        return (end.year - self.start_date.year)

    def get_summary(self):
        return f"{self.course} - {self.institution}"

    def __str__(self):
        return f"{self.course} ({self.institution})"