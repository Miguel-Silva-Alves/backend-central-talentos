import re
from PyPDF2 import PdfReader
import spacy


class PDFExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = self._extract_text()
        self.nlp = spacy.load("pt_core_news_sm")
        self.doc = self.nlp(self.text)

    def _extract_text(self) -> str:
        reader = PdfReader(self.file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    def pdf_with_text(self) -> bool:
        return len(self.text) > 0

    # -------------------------
    # CAMPOS BÁSICOS
    # -------------------------

    def extract_entities(self):
        return [ent.text for ent in self.doc.ents]

    def extract_email(self):
        matches = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", self.text)
        return matches[0] if matches else None

    def extract_phone(self):
        match = re.findall(r"(\(?\d{2}\)?\s?\d{4,5}[-.\s]?\d{4})", self.text)
        return match[0] if match else None

    def extract_name(self):
        lines = [l.strip() for l in self.text.splitlines() if l.strip()]

        blacklist = [
            "habilidades", "qualificações", "formação", "curso",
            "experiência", "objective", "objetivo", "idioma",
            "perfil", "profissional", "graduação", "colégio",
            "ensino", "bacharel", "tecnólogo", "disciplinas",
            "sistemas", "análise", "desenvolvimento"
        ]

        # ---------------------------------------
        # 1) procurar nome nas primeiras linhas
        # ---------------------------------------
        for line in lines[:8]:
            clean = line.replace("•", "").replace("-", " ").strip()

            if any(b in clean.lower() for b in blacklist):
                continue

            # deve ter no mínimo 2 palavras
            parts = clean.split()
            if len(parts) < 2:
                continue

            # ignorar linhas com tamanho absurdo
            if len(clean) > 40:
                continue

            # palavras devem começar com maiúscula ou serem caixa alta
            if all(p[0].isalpha() and (p[0].isupper() or p.isupper()) for p in parts):
                return clean

        # ---------------------------------------
        # 2) tentar spaCy PER, mas só se não for palavra grudada
        # ---------------------------------------
        persons = [
            ent.text.strip()
            for ent in self.doc.ents
            if ent.label_ == "PER"
        ]

        # tentar primeiro nomes com pelo menos 2 palavras
        for p in persons:
            if " " in p and len(p) < 40:
                return p

        # senão pegar nome curto único (ex.: DYLAN)
        for p in persons:
            if len(p.split()) == 1 and p.isalpha() and p.isupper():
                return p

        # ---------------------------------------
        # 3) fallback
        # ---------------------------------------
        for line in lines:
            if (len(line.split()) >= 2
                and not any(c.isdigit() for c in line)
                and not any(b in line.lower() for b in blacklist)):
                return line

        return None



    # -------------------------
    # CAMPOS AVANÇADOS
    # -------------------------

    def extract_age(self):
        """
        Procura padrões como '28 anos', 'Idade: 32', etc.
        """
        match = re.search(r"(\d{2})\s*anos", self.text.lower())
        return int(match.group(1)) if match else None

    def extract_years_experience(self):
        """
        Procura padrões: '5 anos de experiência', 'experiência: 10 anos', etc.
        """
        match = re.search(
            r"(\d{1,2})\s*(anos de experiência|anos experiência|anos exp)",
            self.text.lower(),
        )
        return int(match.group(1)) if match else None

    def extract_current_position(self):
        """
        Tenta achar o cargo atual com heurística baseada em palavras-chave.
        """
        patterns = [
            r"cargo atual[:\- ]*(.+)",
            r"posição atual[:\- ]*(.+)",
            r"atualmente em[:\- ]*(.+)",
            r"atual[:\- ]*(.+)",
        ]
        for pat in patterns:
            match = re.search(pat, self.text, flags=re.IGNORECASE)
            if match:
                # pega só a primeira frase
                pos = match.group(1).split("\n")[0]
                return pos.strip()
        return None

    def extract_skills(self):
        """
        Procura seção 'Habilidades', 'Skills', etc.
        """
        skills_block = re.search(
            r"(habilidades|skills)[:\- ]*(.+?)(\n\n|\Z)",
            self.text,
            flags=re.IGNORECASE | re.DOTALL
        )
        if skills_block:
            items = re.split(r"[,•\n]", skills_block.group(2))
            return [i.strip() for i in items if len(i.strip()) > 1]
        return []

    def extract_companies(self):
        """
        Lista empresas detectadas pelo spaCy (ORG).
        """
        return list({ent.text for ent in self.doc.ents if ent.label_ == "ORG"})

    def extract_location(self):
        """
        Extrai a localização do candidato.
        Tenta padrões explícitos como:
        - São Paulo - SP
        - Curitiba/PR
        - Belo Horizonte MG
        - Recife, PE
        E depois tenta spaCy (LOC/GPE).
        """

        # -------------------------
        # 1) padrões clássicos "Cidade - UF", "Cidade/UF", "Cidade, UF"
        # -------------------------
        patterns = [
            r"([A-ZÁ-Úa-zá-ú\s]+)[\-\/,\s]+(SP|RJ|MG|ES|RS|SC|PR|BA|PE|CE|GO|DF|AM|PA|PB|RN|SE|MT|MS|RO|RR|AC|AP|MA|TO)",
        ]

        for pat in patterns:
            match = re.search(pat, self.text)
            if match:
                cidade = match.group(1).strip()
                uf = match.group(2).strip()
                return f"{cidade} - {uf}"

        # -------------------------
        # 2) Lista básica de cidades do Brasil (curta, mas útil)
        # -------------------------
        cidades = [
            "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Brasília", "Curitiba",
            "Salvador", "Fortaleza", "Recife", "Porto Alegre", "Manaus", "Belém",
            "Goiânia", "Campinas", "Florianópolis", "Vitória", "São Luís"
        ]

        for cidade in cidades:
            if cidade.lower() in self.text.lower():
                return cidade

        # -------------------------
        # 3) spaCy fallback (LOC/GPE)
        # -------------------------
        locs = [
            ent.text.strip()
            for ent in self.doc.ents
            if ent.label_ in ("LOC", "GPE")
        ]

        # priorizar itens com pelo menos 4 letras (evita siglas soltas)
        for loc in locs:
            if len(loc) >= 4:
                return loc

        return None


    # -------------------------
    # RESUMO FINAL
    # -------------------------

    def profile_summary(self, info: dict):
        nome = info.get("nome")
        idade = info.get("idade")
        exp = info.get("anos_experiencia")
        cargo = info.get("cargo_atual") or "sem posição atual"
        habilidades = info.get("habilidades", []) or []
        email = info.get("email")
        telefone = info.get("telefone")

        # ---- 1. Validar nome ----
        def nome_valido(n: str | None) -> bool:
            if not n:
                return False
            # não pode ter símbolos típicos de listas/tech
            if any(sym in n for sym in ["•", ";", "/", "|"]):
                return False
            # não pode ser só tecnologias
            tech_keywords = ["python", "java", "sql", "react", "javascript", "html"]
            if any(t in n.lower() for t in tech_keywords):
                return False
            # precisa ter pelo menos 2 palavras
            if len(n.split()) < 2:
                return False
            # nome não pode ter mais de 40 caracteres
            if len(n) > 40:
                return False
            return True

        nome_ok = nome if nome_valido(nome) else None

        # ---- 2. Criar resumo ----
        partes = []

        # Nome
        if nome_ok:
            partes.append(nome_ok)
        else:
            partes.append("Candidato")

        # Idade
        if idade:
            partes.append(f"{idade} anos")

        # Experiência
        if exp:
            partes.append(f"{exp} anos de experiência")

        # Cargo
        if cargo:
            partes.append(f"— atualmente em '{cargo}'")

        resumo = ", ".join([p for p in partes if p])

        # ---- 3. Enriquecer com habilidades ----
        if habilidades:
            # pega só coisas úteis (com separação clara e tamanho aceitável)
            clean_hab = [
                h.replace("–", "").replace("•", "").strip()
                for h in habilidades
                if len(h) < 40 and not h.lower().startswith(("qualificações", "formação"))
            ]

            # tentar detectar tecnologias
            techs = []
            for h in clean_hab:
                # separar por ; ou por palavra camelCase grudada
                for part in re.split(r"[;,\s]+", h):
                    if len(part) <= 2:
                        continue
                    if re.match(r"^[A-Za-z]+$", part):
                        techs.append(part)

            techs = list(dict.fromkeys(techs))  # remover duplicados

            if techs:
                resumo += f". Competências: {', '.join(techs[:8])}"

        # ---- 4. Contato ----
        contato = []
        if telefone:
            contato.append(telefone)
        if email:
            contato.append(email)

        if contato:
            resumo += f". Contato: {', '.join(contato)}."

        return resumo.strip()


    # -------------------------
    # RESPOSTA FINAL PARA API
    # -------------------------

    def extract_resume_info(self):
        data =  {
            "nome": self.extract_name(),
            "email": self.extract_email(),
            "telefone": self.extract_phone(),
            "idade": self.extract_age(),
            "anos_experiencia": self.extract_years_experience(),
            "cargo_atual": self.extract_current_position(),
            "habilidades": self.extract_skills(),
            "location": self.extract_location(),
            "empresas": self.extract_companies(),
        }

        data["resumo"] = self.profile_summary(data)
        return data
