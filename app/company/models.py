from django.db import models
from django.core.validators import RegexValidator
from datetime import date
from typing import List, Dict
import re


class Company(models.Model):
    """
    Representa uma empresa com nome e CNPJ.
    """

    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)  # Ex: 00.000.000/0000-00
    created_at = models.DateTimeField(auto_now=True)
    user_creator = models.ForeignKey(
        "access.User",
        on_delete=models.CASCADE,
        related_name="companies_created"  # nome reverso único
    )

    def __str__(self):
        return self.name

    # --- Métodos do diagrama ---

    def validate_cnpj(self) -> bool:
        """
        Valida o formato e os dígitos verificadores do CNPJ.
        Retorna True se for válido, False caso contrário.
        """
        cnpj = re.sub(r'\D', '', self.cnpj)

        if len(cnpj) != 14:
            return False

        # Elimina CNPJs com todos os dígitos iguais
        if cnpj == cnpj[0] * 14:
            return False

        # Cálculo dos dígitos verificadores
        def calc_dv(cnpj_base, pesos):
            soma = sum(int(cnpj_base[i]) * pesos[i] for i in range(len(pesos)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        # Primeiro dígito verificador
        dv1 = calc_dv(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        # Segundo dígito verificador
        dv2 = calc_dv(cnpj[:12] + dv1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])

        return cnpj[-2:] == dv1 + dv2

    def get_summary(self) -> str:
        """
        Retorna um resumo textual da empresa.
        """
        return f"{self.name} (CNPJ: {self.cnpj})"

class Candidate(models.Model):
    """
    Representa um candidato a uma vaga de emprego.
    """

    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    current_position = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{8,15}$', 'Número de telefone inválido.')]
    )
    years_experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_creator = models.ForeignKey(
        "access.User",
        on_delete=models.CASCADE,
        related_name="candidates_created"
    )

    def __str__(self):
        return self.name

    # --- Métodos do diagrama ---

    def get_age(self) -> int:
        """
        Retorna a idade atual do candidato com base na data de nascimento.
        """
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def validate_email(self) -> bool:
        """
        Valida o formato do e-mail usando regex.
        Retorna True se for válido, False caso contrário.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, self.email) is not None

    def profile_summary(self) -> str:
        """
        Retorna um resumo textual do perfil do candidato.
        """
        return (
            f"{self.name}, {self.get_age()} anos, "
            f"{self.years_experience} anos de experiência — "
            f"atualmente em '{self.current_position or 'sem posição atual'}'."
        )

class Profile(models.Model):
    """
    Representa um perfil/cluster,
    que pode estar vinculado a múltiplos candidatos.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    top_skills = models.TextField(
        help_text="Lista de habilidades principais separadas por vírgula."
    )
    candidates = models.ManyToManyField(
        "candidate.Candidate",  # app_label.ModelName
        related_name="profiles",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # --- Métodos do diagrama UML ---

    def get_summary(self) -> str:
        """
        Retorna um resumo textual do perfil.
        """
        skills = ', '.join(self.list_skills()) or "sem habilidades definidas"
        return f"{self.name}: {self.description or 'Sem descrição'} | Habilidades: {skills}"

    def update_description(self, description: str) -> None:
        """
        Atualiza a descrição do perfil.
        """
        self.description = description
        self.save(update_fields=["description"])

    def add_skill(self, skill: str) -> None:
        """
        Adiciona uma nova skill à lista de top_skills.
        """
        skills = self.list_skills()
        if skill not in skills:
            skills.append(skill)
            self.top_skills = ", ".join(skills)
            self.save(update_fields=["top_skills"])

    def list_skills(self) -> List[str]:
        """
        Retorna a lista de skills como uma lista Python.
        """
        return [s.strip() for s in self.top_skills.split(",") if s.strip()]

    def add_candidate(self, candidate) -> None:
        """
        Adiciona um candidato ao perfil (relação ManyToMany).
        """
        self.candidates.add(candidate)

    def remove_candidate(self, candidate) -> None:
        """
        Remove um candidato vinculado ao perfil.
        """
        self.candidates.remove(candidate)

    def list_candidates(self):
        """
        Retorna a lista de candidatos associados ao perfil.
        """
        return self.candidates.all()