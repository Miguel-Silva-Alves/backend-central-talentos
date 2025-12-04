from company.models import Candidate, FileCandidate
from company.serializer import CandidateSerializer
from rest_framework import viewsets
from rh.models import File

# Common
from common.token import TokenValidator
from common.response import ResponseDefault, CreatedRequest, BadRequest, NotFound, UnauthorizedRequest


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    @TokenValidator.require_token
    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
        except Exception:
            return NotFound("candidate not found")

        serializer = self.get_serializer(user)
        return ResponseDefault("candidate retrieved", {"candidate": serializer.data})


    @TokenValidator.require_token
    def list(self, request, *args, **kwargs):
        result = []
        candidates = Candidate.objects.filter(user_creator__company=request.user.company)

        for cand in candidates:

            files = FileCandidate.objects.filter(candidate=cand)

            data_files = [
                {
                    "id": fc.file.id,
                    "name": fc.file.name,
                    "size_mb": fc.file.size_mb,
                    "download_url": fc.file.download_url,   # <- agora funciona
                }
                for fc in files
            ]

            # monta o candidato manualmente
            result.append({
                "id": cand.id,
                "name": cand.name,
                "email": cand.email,
                "birth_date": cand.birth_date,
                "current_position": cand.current_position,
                "years_experience": cand.years_experience,
                "location": cand.location,
                "phone": cand.phone,
                "candidate_description": cand.profile_summary(),
                "key_skills": cand.key_skills(),
                "files_uploaded": data_files,
            })

        return ResponseDefault("list of candidates", {"candidates": result})


    @TokenValidator.require_token
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        file_ids = data.pop("files", [])

        # 1️⃣ Valida os dados sem criar nada
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return BadRequest(serializer.errors)

        # 2️⃣ Cria o candidate MANUALMENTE
        candidate = Candidate.objects.create(
            name=serializer.validated_data["name"],
            email=serializer.validated_data["email"],
            birth_date=serializer.validated_data["birth_date"],
            current_position=serializer.validated_data.get("current_position"),
            years_experience=serializer.validated_data.get("years_experience", 0),
            location=serializer.validated_data.get("location"),
            phone=serializer.validated_data["phone"],
            user_creator=request.user,  # vem do token
            profile_resume=serializer.validated_data["profile_resume"],
        )

        # 3️⃣ Vincula arquivos (regra de negócio → view)
        for file_id in file_ids:
            try:
                f = File.objects.get(pk=file_id)
                FileCandidate.objects.create(candidate=candidate, file=f)
            except File.DoesNotExist:
                continue

        # 4️⃣ Retorno
        output = CandidateSerializer(candidate).data
        return CreatedRequest("candidate created", {"candidate": output})
