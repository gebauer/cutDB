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
            if True: # g.name in ['COL'+'95']:
                    # Finding Cys after N-Pro domain
                g.sequence = g.sequence.replace (" ","")
                
                g.save()
            
                
             