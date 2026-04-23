import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import ask_spark

@csrf_exempt
def chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        if not user_message:
            return JsonResponse({'error': 'message is required'}, status=400)

        answer = ask_spark(user_message)
        return JsonResponse({'answer': answer})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
