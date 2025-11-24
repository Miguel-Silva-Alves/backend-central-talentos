from django.db import models
from access.models import User
from company.models import Candidate
import numpy as np
from numpy.linalg import norm
from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField

from rh.models import File  # seu modelo de arquivos
from common.embedding import create_embedding  # função que você escreveu


def cosine_sim(v1, v2):
    """Cosine similarity entre dois vetores."""
    v1 = np.array(v1)
    v2 = np.array(v2)
    return float(np.dot(v1, v2) / (norm(v1) * norm(v2)))


class Queries(models.Model):
    ask = models.TextField("Pergunta", blank=False)
    answer = models.TextField("Resposta", blank=True, null=True)

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

    # -------------------------
    # Métodos
    # -------------------------
    def reply(self, answer: str):
        """Define a resposta da query."""
        self.answer = answer
        self.save(update_fields=["answer", "updated_at"])

    def is_answered(self) -> bool:
        """Verifica se a query já foi respondida."""
        return bool(self.answer and self.answer.strip())

    def create_indication(self, candidate):
        """Cria uma indicação associada a esta query e a um candidato."""
        from .models import Indication  # evita import circular
        return Indication.objects.create(candidate=candidate, query=self)

    # -------------------------
    # MATCH SEMÂNTICO (LLM)
    # -------------------------
    def find_best_candidates(self, job_description: str, top_n: int = 5):
        """
        Gera embedding da descrição da vaga,
        compara com todos os candidatos processados,
        e retorna os melhores matches.
        """

        # Embedding da vaga
        job_emb = create_embedding(job_description)

        candidates = File.objects.filter(processed=True)
        scored = []

        for c in candidates:
            # Ignorar candidatos sem embedding
            if not c.embedding:
                continue

            try:
                sim = cosine_sim(job_emb, c.embedding)
            except Exception:
                continue

            scored.append({
                "candidate": c,
                "similaridade": sim,
            })

        # Ordena do maior para o menor
        scored.sort(key=lambda x: x["similaridade"], reverse=True)

        return scored[:top_n]


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