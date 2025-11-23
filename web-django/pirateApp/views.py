import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import HuntInstruction
from .oracle_client import fetch_next_direction, OracleAPIError


@require_http_methods(["GET"])
def list_hunt_instructions(request):
    data = [
        {
            "instruction_id": h.instruction_id,
            "title": h.title,
            "direction": h.direction,
            "distance_nm": h.distance_nm,
            "description": h.description,
            "image_url": h.image_url,
            "next_oracle_id": (h.raw_payload or {}).get("nextID")
        }
        for h in HuntInstruction.objects.order_by("instruction_id")
    ]
    return JsonResponse({"instructions": data})

def index(request):
    return redirect('/compass/')

@csrf_exempt
@require_http_methods(["POST"])
def fetch_and_save_instruction(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Body JSON invalid"}, status=400)

# Create your views here.
def compass(request):
    context = {
        "instructions": Instruction.objects.order_by("created_at"),
    }

    if request.method == "POST":
        last_id_raw = (request.POST.get("last_id") or "").strip()

        if not last_id_raw.isdigit():
            messages.error(request, "Instruction ID must be a positive integer.")
            return render(request, "pirateApp/compass_hard.html", context)

        last_id = int(last_id_raw)

        try:
            data = fetch_next_instruction(last_id)

            # AICI mapezi ce primești de la oracle.
            # Presupunere rezonabilă de chei; ajustezi după payload-ul real:
            new_id = int(data["id"])
            title = data.get("title", f"Instruction {new_id}")
            direction = data.get("direction", "").lower()
            distance = int(data.get("distance", 0))
            description = data.get("description", "")
            image_url = data.get("image", "") or data.get("image_url", "")

            prev_obj = Instruction.objects.filter(id=last_id).first()

            instr, created = Instruction.objects.update_or_create(
                id=new_id,
                defaults={
                    "title": title,
                    "direction": direction,
                    "distance": distance,
                    "description": description,
                    "image_url": image_url,
                    "previous_instruction": prev_obj,
                }
            )

            if created:
                messages.success(request, f"Fetched new instruction #{instr.id}.")
            else:
                messages.info(request, f"Instruction #{instr.id} updated.")

        except requests.HTTPError as e:
            messages.error(request, f"Oracle error: {e.response.status_code}")
        except requests.RequestException:
            messages.error(request, "Could not reach the oracle. Try again.")
        except (KeyError, ValueError, TypeError):
            messages.error(request, "Oracle returned unexpected data format.")

        context["instructions"] = Instruction.objects.order_by("created_at")

    return render(request, "pirateApp/compass.html", context)