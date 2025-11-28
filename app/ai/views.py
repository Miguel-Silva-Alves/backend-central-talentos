from rest_framework import viewsets
from rest_framework.decorators import action

from ai.models import Queries
from ai.serializer import QuerieSerializer
from company.models import Candidate, FileCandidate
from rh.models import File

# Swagger
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Common
from common.token import TokenValidator
from common.response import ResponseDefault, BadRequest
from common.embedding import create_embedding, cosine_sim


class QuerieViewSet(viewsets.ModelViewSet):
    queryset = Queries.objects.all()
    serializer_class = QuerieSerializer
    
    @action(detail=False, methods=['post'], url_path='prompt')
    @TokenValidator.require_token
    def prompt(self, request):
        prompt_text = request.data.get('prompt')

        if not prompt_text:
            return BadRequest("Nenhum prompt enviado.")

        # salva a pergunta
        Queries.objects.create(
            ask=prompt_text,
            user=request.user
        )

        # ➤ 1) gera embedding da pergunta
        query_emb = create_embedding(prompt_text)

        # ➤ 2) busca todos arquivos associados a candidatos
        file_links = FileCandidate.objects.select_related("file", "candidate")

        response_list = []

        for link in file_links:
            file = link.file

            if type(file) != File:
                continue
            
            # garante que o arquivo tenha embedding
            if not file.embedding:
                continue

            score = cosine_sim(query_emb, file.embedding)

            response_list.append({
                "candidate_id": link.candidate.id,
                "candidate_name": link.candidate.name,
                "candidate_description": link.candidate.profile_summary(),
                "file_id": file.id,
                "key_skills": file.word_cloud[:5],
                "score": score,
            })

        # ➤ 3) agrega por candidato (pega o arquivo com maior score)
        candidates_final = {}
        for item in response_list:
            cid = item["candidate_id"]
            if cid not in candidates_final or item["score"] > candidates_final[cid]["score"]:
                candidates_final[cid] = item

        # ordena por score
        ordered = sorted(candidates_final.values(), key=lambda x: x["score"], reverse=True)

        # monta resposta
        final = []
        for item in ordered:
            cand = Candidate.objects.get(pk=item["candidate_id"])

            final.append({
                "id": cand.id,
                "name": cand.name,
                "email": cand.email,
                "score": item["score"],
                "key_skills": item["key_skills"],
                "candidate_description": item["candidate_description"],
            })

        return ResponseDefault(
            message="Candidatos ranqueados por similaridade",
            data={"results": final}
        )

