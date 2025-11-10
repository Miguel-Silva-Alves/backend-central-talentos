import re
from PyPDF2 import PdfReader
import spacy


class PDFExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = self._extract_text()
        self.nlp = spacy.load("pt_core_news_sm")

    def _extract_text(self) -> str:
        reader = PdfReader(self.file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()

    def pdf_with_text(self) -> bool:
        return len(self.text) > 0

    def extract_entities(self):
        """Extrai entidades genéricas via spaCy"""
        doc = self.nlp(self.text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def extract_email(self):
        """Extrai e-mail com regex"""
        matches = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", self.text)
        return matches[0] if matches else None

    def extract_phone(self):
        """Extrai telefones brasileiros comuns"""
        matches = re.findall(
            r"(\(?\d{2}\)?\s?\d{4,5}[-.\s]?\d{4})", self.text
        )
        return matches[0] if matches else None

    def extract_name(self):
        """Tenta extrair o nome da pessoa com heurística + spaCy"""
        doc = self.nlp(self.text)
        # pega apenas entidades reconhecidas como PESSOA
        persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PER"]
        if persons:
            # geralmente o primeiro nome no texto é o candidato
            return persons[0]

        # fallback: primeira linha com mais de uma palavra e sem números
        for line in self.text.splitlines():
            if len(line.split()) >= 2 and not any(c.isdigit() for c in line):
                return line.strip()
        return None

    def extract_resume_info(self):
        return {
            "nome": self.extract_name(),
            "email": self.extract_email(),
            "telefone": self.extract_phone(),
        }