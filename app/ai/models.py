from django.db import models
from access.models import User
from company.models import Candidate
class Queries(models.Model):
    ask = models.TextField("Pergunta", blank=False)
    answer = models.TextField("Resposta", blank=True, null=True)

    # FK para o usuário que fez a pergunta
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="queries",
        verbose_name="Usuário"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Query"
        verbose_name_plural = "Queries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Query #{self.id} - {self.ask[:50]}..."

    # ---- Métodos do diagrama ----
    def reply(self, answer: str):
        """Define a resposta da query."""
        self.answer = answer
        self.save(update_fields=["answer", "updated_at"])

    def is_answered(self) -> bool:
        """Verifica se a query foi respondida."""
        return bool(self.answer and self.answer.strip())

    def create_indication(self, candidate):
        """Cria uma indicação associada a esta query e a um candidato."""
        indication = Indication.objects.create(candidate=candidate, query=self)
        return indication

class Indication(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # FK para a query que originou a indicação
    query = models.ForeignKey(
        Queries,
        on_delete=models.CASCADE,
        related_name="indications",
        verbose_name="Query"
    )

    # FK para o candidato indicado
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="indications",
        verbose_name="Candidato"
    )

    class Meta:
        verbose_name = "Indicação"
        verbose_name_plural = "Indicações"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Indicação #{self.id} - {self.candidate}"

    # --- Métodos do diagrama ---
    def assign_candidate(self, candidate):
        """Associa um candidato a esta indicação."""
        self.candidate = candidate
        self.save(update_fields=["candidate"])

    def get_candidate(self):
        """Retorna o candidato associado."""
        return self.candidate