import requests
from django.shortcuts import render
from django.contrib import messages
from .models import Instruction

ORACLE_BASE = "https://coderum-2025-pirates-baace2h8crd9btg4.canadacentral-01.azurewebsites.net"
# În PDF zice că vei primi instrucțiuni în timp real despre URL.
# Păstrează funcția asta și ajustezi path-ul când îl afli.
def build_oracle_url(last_id: int) -> str:
    # EXEMPLU posibil (NU garantat):
    # return f"{ORACLE_BASE}/direction/set-sail/{last_id}"
    # sau:
    # return f"{ORACLE_BASE}/direction/set-sail?lastInstructionId={last_id}"
    return f"{ORACLE_BASE}/direction/set-sail/{last_id}"


def fetch_next_instruction(last_id: int) -> dict:
    url = build_oracle_url(last_id)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


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