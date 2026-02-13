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

                    f_t, created = feature_type.objects.get_or_create(name='N-Propeptide')
                    feat_NPro = feature.objects.filter(type=f_t,gene=g)
                    if (feat_NPro):
                        feat_NPro = feat_NPro[0]
                        offset = feat_NPro.end()-3

                        # Finding N-Cys-ProPep

                        reg_exprs = ["^(?:G..).{1,5}(?P<CCysProPep>C)",
                                    ]
                        print ("Searching C-Cys-ProPeps ... trying ...", end='')
                        searchstring = g.sequence[feat_NPro.end()-3:]
                        print (g.name, end='')
                        found = False
                        for idx, reg_expr in enumerate (reg_exprs):
                            print ("{}".format(idx),end="")
                            reg = re.compile (reg_expr)
                            iterator = reg.finditer(searchstring) 
                            for match in iterator:
                                f_t, created = feature_type.objects.get_or_create(name='C-Cys-ProPep')
                                feat = feature.objects.filter(type=f_t,gene=g)
                                region = str(match.start('CCysProPep') +1 +offset) + '..' + str( match.end('CCysProPep')+offset)
                                if not feat:
                                    feat = feature(name='Cysteine knot', type=f_t, gene=g, region=region)
                                    feat.save()
                                else:
                                    feat.update(region=region)
                                print ("found {}".format(region))
                                found = True
                            if found == True:
                                break
                        if found == False:
                            print (" not found!")




                                
                #g.save()
            
                
             