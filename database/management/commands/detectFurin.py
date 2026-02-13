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


                    # Finding N-Cys-ProPep

                reg_exprs = ["(?P<Furin>RGD)",
                            ]
                print ("Searching ... trying ...", end='')
                searchstring = g.sequence
                print (g.name, end='')
                found = False
                f_t, created = feature_type.objects.get_or_create(name='RGD_motif')
                if created:
                    f_t.description = "predicted integrin binding site (RGD)"
                    f_t.color="#028cfd"
                    f_t.save()

                print ("Deleting old Furin entries from {}".format(g))
                feature.objects.filter(type=f_t, gene=g, manually_edited=False).delete()

                for idx, reg_expr in enumerate (reg_exprs):
                    print ("{}".format(idx),end="")
                    reg = re.compile (reg_expr)
                    iterator = reg.finditer(searchstring) 
                    for match in iterator:
                        feat = feature.objects.filter(type=f_t,gene=g)
                        region = str(match.start('Furin') +1 ) + '..' + str( match.end('Furin'))
                        feat = feature(name='RGD', type=f_t, gene=g, region=region, modeOfGeneration=feature.REGEXP )
                        feat.save()
                        print ("found {}".format(region))
                        found = True
