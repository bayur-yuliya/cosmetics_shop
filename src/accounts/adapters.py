from allauth.account.adapter import DefaultAccountAdapter
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse


class AjaxFriendlyAccountAdapter(DefaultAccountAdapter):
    def respond(self, request, response):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return super().respond(request, response)

        if isinstance(response, HttpResponseRedirect):
            return JsonResponse({
                "success": True,
                "redirect": response.url or reverse('some_default_view'),
            })

        if hasattr(response, 'context_data') and 'form' in response.context_data:
            form = response.context_data['form']
            if form.non_field_errors():

                return JsonResponse({
                    "non_field_errors": [str(e) for e in form.non_field_errors()]
                }, status=400)

            field_errors = {}
            for field in form:
                if field.errors:
                    field_errors[field.name] = [str(e) for e in field.errors]
            if field_errors:
                return JsonResponse(field_errors, status=400)
        return JsonResponse({"error": "Неизвестная ошибка"}, status=400)
