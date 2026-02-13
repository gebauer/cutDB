from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, feature_type, clade, project_settings


from Bio import SeqIO

import requests, sys
import os, re

class Command(BaseCommand):
    help = 'Count how many hyp could be possible'

    def add_arguments(self, parser):
          #parser.add_argument('file', nargs='+', type=str)
          pass

    def handle(self, *args, **options):
        for g in gene.objects.all():
            if g.name[0:3] == 'COL' and g.name[0:4] != 'COL-':
                # g.name = ("COL-{}").format(int(g.name[3:]))
                # g.save()
                pass
            else:
                print (g.name, end=" = ")
                g.name = g.name.upper()
                print (g.name)
                g.save()