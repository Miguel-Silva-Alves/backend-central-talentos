from django.db import models
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