import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import HuntInstruction, PasswordGuess
from .oracle_client import fetch_next_direction, OracleAPIError, check_password


@require_http_methods(["GET"])
def index(request):
    return redirect("/compass/")


@require_http_methods(["GET", "POST"])
def compass(request):
    """
    HARD mode, exact ca în PDF:
    - Form cu UN SINGUR input: last_instruction_id
    - Backend calculează oracle_id automat:
        * dacă last_id == 0 => oracle_id = "set-sail", next_number = 1
        * altfel => oracle_id = DB[last_id].raw_payload["nextID"], next_number = last_id + 1
    - Face request la Oracle, salvează în DB, apoi afișează logul.
    """
    context = {
        "hunt_instructions": HuntInstruction.objects.order_by("instruction_id"),
        "error": None,
        "success": None,
    }

    if request.method == "POST":
        last_id_raw = (request.POST.get("last_id") or "").strip()

        if not last_id_raw.isdigit():
            context["error"] = "Instruction ID must be a non-negative integer."
            return render(request, "pirateApp/compass.html", context)

        last_id = int(last_id_raw)

        # determinăm oracle_id + next instruction_number
        if last_id == 0:
            oracle_id = "set-sail"
            instruction_number = 1
        else:
            prev = HuntInstruction.objects.filter(instruction_id=last_id).first()
            if not prev:
                context["error"] = f"No instruction with ID={last_id} in DB."
                return render(request, "pirateApp/compass.html", context)

            oracle_id = (prev.raw_payload or {}).get("nextID")
            if not oracle_id:
                context["error"] = f"Instruction {last_id} has no nextID. Maybe you reached the end?"
                return render(request, "pirateApp/compass.html", context)

            instruction_number = last_id + 1

        # apel Oracle
        try:
            data = fetch_next_direction(oracle_id, instruction_number)
        except OracleAPIError as e:
            context["error"] = str(e)
            return render(request, "pirateApp/compass.html", context)

        # salvare DB
        obj, created = HuntInstruction.objects.update_or_create(
            instruction_id=instruction_number,
            defaults={
                "title": data.get("title", ""),
                "direction": data.get("direction", ""),
                "distance_nm": int(data.get("distanceInMeters", 0)),  # păstrăm metri aici
                "description": data.get("instructionText", ""),
                "image_url": data.get("pictureUrl", ""),
                "raw_payload": data,
            }
        )

        context["success"] = (
            f"Fetched instruction #{obj.instruction_id}. "
            f"Next oracle_id is '{(data.get('nextID') or '')}'."
        )
        context["hunt_instructions"] = HuntInstruction.objects.order_by("instruction_id")

    return render(request, "pirateApp/compass.html", context)


@require_http_methods(["GET"])
def list_hunt_instructions(request):
    data = [
        {
            "instruction_id": h.instruction_id,
            "title": h.title,
            "direction": h.direction,
            "distanceInMeters": h.distance_nm,
            "instructionText": h.description,
            "pictureUrl": h.image_url,
            "oracle_id": (h.raw_payload or {}).get("id"),
            "nextID": (h.raw_payload or {}).get("nextID"),
        }
        for h in HuntInstruction.objects.order_by("instruction_id")
    ]
    return JsonResponse({"instructions": data})


@csrf_exempt
@require_http_methods(["POST"])
def fetch_and_save_instruction(request):
    """
    Păstrăm endpointul tău JSON (merge cu Postman/React dacă vrei),
    dar PDF-ul e satisfăcut de /compass cu 1 input.
    """
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Body JSON invalid"}, status=400)

    instruction_number = body.get("instruction_number")
    oracle_id = body.get("oracle_id")

    if instruction_number is None or oracle_id is None:
        return JsonResponse(
            {"error": "Trebuie să trimiți instruction_number și oracle_id"},
            status=400
        )

    try:
        data = fetch_next_direction(str(oracle_id), int(instruction_number))
    except OracleAPIError as e:
        return JsonResponse({"error": str(e)}, status=400)

    obj, _ = HuntInstruction.objects.update_or_create(
        instruction_id=int(instruction_number),
        defaults={
            "title": data.get("title", ""),
            "direction": data.get("direction", ""),
            "distance_nm": int(data.get("distanceInMeters", 0)),
            "description": data.get("instructionText", ""),
            "image_url": data.get("pictureUrl", ""),
            "raw_payload": data,
        }
    )

    return JsonResponse({
        "saved": True,
        "next_oracle_id": data.get("nextID"),
        "instruction": {
            "instruction_id": obj.instruction_id,
            "title": obj.title,
            "direction": obj.direction,
            "distanceInMeters": obj.distance_nm,
            "description": obj.description,
            "pictureUrl": obj.image_url,
        }
    })


@require_http_methods(["GET", "POST"])
def treasure(request):
    """
    Pagina finală:
    - 4 inputuri (d1,d2,d3,d4)
    - GET la oracle /check-password/abcd
    - salvează fiecare încercare în DB
    - afișează rezultatul + istoricul încercărilor
    """
    context = {
        "result": None,
        "error": None,
        "guesses": PasswordGuess.objects.order_by("-created_at"),
    }

    if request.method == "POST":
        d1 = (request.POST.get("d1") or "").strip()
        d2 = (request.POST.get("d2") or "").strip()
        d3 = (request.POST.get("d3") or "").strip()
        d4 = (request.POST.get("d4") or "").strip()

        digits = [d1, d2, d3, d4]

        # validare: exact câte o cifră per input
        if not all(len(x) == 1 and x.isdigit() for x in digits):
            context["error"] = "All four fields must be single digits (0-9)."
            return render(request, "pirateApp/treasure.html", context)

        code = "".join(digits)

        try:
            data = check_password(code)
        except OracleAPIError as e:
            context["error"] = str(e)
            return render(request, "pirateApp/treasure.html", context)

        # interpretăm răspunsul
        # presupunere rezonabilă: oracle trimite un mesaj și/sau un flag
        message = data.get("message") or data.get("instructionText") or str(data)
        is_correct = bool(data.get("isCorrect") or data.get("correct") or data.get("success"))

        PasswordGuess.objects.create(
            code=code,
            is_correct=is_correct,
            message=message,
            raw_payload=data,
        )

        context["result"] = {
            "code": code,
            "is_correct": is_correct,
            "message": message,
        }
        context["guesses"] = PasswordGuess.objects.order_by("-created_at")

    return render(request, "pirateApp/treasure.html", context)