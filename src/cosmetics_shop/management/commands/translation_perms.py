from django.contrib.auth.models import Permission
from django.core.management import BaseCommand
from django.utils.translation import activate
from django.utils.translation import gettext as _


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        activate("ru")

        action_templates = {
            "add": "Can add %(name)s",
            "change": "Can change %(name)s",
            "delete": "Can delete %(name)s",
            "view": "Can view %(name)s",
        }

        updated_count = 0

        for perm in Permission.objects.all():
            action = perm.codename.split("_")[0]

            if action not in action_templates:
                continue

            model_class = perm.content_type.model_class()
            if model_class:
                model_name = model_class._meta.verbose_name
            else:
                model_name = perm.content_type.model

            template = action_templates[action]
            translated_template = _(template)

            new_name = translated_template % {"name": model_name}

            if perm.name != new_name:
                perm.name = new_name
                perm.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully! Updated {updated_count} permissions.")
        )
