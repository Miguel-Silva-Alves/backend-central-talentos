import json
import re
from openai import OpenAI
from project import settings


class GPTClient:
    def _safe_json_extract(self, text: str) -> dict:
        """
        Corrige respostas da IA que vêm com texto extra,
        e tenta extrair somente o JSON.
        """

        # tenta direto
        try:
            return json.loads(text)
        except:
            pass

        # tenta pegar apenas o trecho entre { ... }
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except:
                pass

        raise {"error": "Não foi possível extrair um JSON válido da resposta da IA."}
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.prompt = """
        Você é um extrator de informações de currículos.

        Receba um texto e retorne EXCLUSIVAMENTE um JSON válido com os seguintes campos:

        {
          "name": "",
          "email": "",
          "birth_date": "",
          "current_position": "",
          "years_experience": 0,
          "location": "",
          "phone": "",
          "candidate_description": "",
          "key_skills": []
        }

        Se alguma informação não estiver presente no texto, retorne como null.
        Não invente informações.
        """

    def extract(self, text: str) -> dict:
        """Extrai informações estruturadas de um currículo em texto."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text}
            ]
        )

        content = response.choices[0].message.content
        return self._safe_json_extract(content)
