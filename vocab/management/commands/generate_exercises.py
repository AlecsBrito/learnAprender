from django.core.management.base import BaseCommand, CommandError
from vocab.models import Vocabulary
from vocab.utils import generate_exercises_for_vocab
from exercises.models import Exercise
from django.contrib.auth import get_user_model
from django.db import transaction


class Command(BaseCommand):
    help = 'Generate exercises from vocabulary entries. Use --all or --pk <id>'

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', help='Generate exercises for all vocabulary')
        parser.add_argument('--pk', type=int, help='Primary key of a Vocabulary entry to generate from')
        parser.add_argument('--user', type=str, help='Username to assign as created_by (optional)')

    def handle(self, *args, **options):
        all_flag = options.get('all')
        pk = options.get('pk')
        username = options.get('user')

        User = get_user_model()
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' does not exist")
        else:
            user = User.objects.first()
            if not user:
                raise CommandError('No users available in database; please create a user or pass --user')

        items = []
        if all_flag:
            items = list(Vocabulary.objects.all())
        elif pk:
            try:
                items = [Vocabulary.objects.get(pk=pk)]
            except Vocabulary.DoesNotExist:
                raise CommandError(f'Vocabulary with pk={pk} not found')
        else:
            raise CommandError('Specify --all or --pk <id>')

        total_created = 0
        with transaction.atomic():
            for v in items:
                gens = generate_exercises_for_vocab(v, distractor_pool=list(Vocabulary.objects.exclude(pk=v.pk)[:50]))
                for ex in gens:
                    ex.created_by = user
                    ex.save()
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(f'Generated {total_created} exercises from {len(items)} vocabulary items'))
