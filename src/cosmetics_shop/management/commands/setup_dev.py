from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs all necessary commands in one chain"

    def handle(self, *args, **options):
        self.stdout.write("Starting the full setup of the project...")

        commands = [
            ("migrate", {"settings": "config.settings.dev"}),
            # ("collectstatic", {"interactive": False}),
            ("translation_perms", {}),
            ("create_groups", {}),
            ("create_info", {}),
            ("add_superuser_perm", {}),
        ]

        for cmd_name, cmd_options in commands:
            self.stdout.write(f"Run: {cmd_name}...")
            call_command(cmd_name, **cmd_options)

        self.stdout.write(self.style.SUCCESS("Successfully!"))
