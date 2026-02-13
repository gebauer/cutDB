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
        f_t1 = feature_type.objects.get (name='col1_domain')
        for g in gene.objects.all():
            if g.name in ['COL-126']:
                print ("== Analysing: {}".format(g.name))
                col_feat = g.feature_set.filter(type = f_t1)
                if col_feat:

                    reg_exprs = ["(?P<NPro>(?:G..){7,}).{5,14}(?P<Cys>C.{2,5}C).{1,3}G",
                                "(?P<NPro>(?:G..){7,}).{5,14}[^C]{6}(?P<Cys>C).{1,3}G"

                                ]
                    # print (g.sequence[:col_feat[0].start()])
                    NProFound = False
                    for idx, reg_expr in enumerate (reg_exprs):
                        reg = re.compile (reg_expr)
                        iterator = reg.finditer(g.sequence[:col_feat[0].start()]) 
                        for match in iterator:
                            f_t, created = feature_type.objects.get_or_create(name='N-Propeptide')
                            feat_NPro = feature.objects.filter(type=f_t,gene=g)
                            region = str(match.start('NPro')+1) + '..' + str(match.end('NPro'))
                            if not feat_NPro:
                                feat_NPro = feature(name='N-Propeptide', type=f_t, gene=g, region=region)
                                feat_NPro.save()
                            else:
                                feat_NPro.update(region=region)
                                feat_NPro = feat_NPro[0]
                            print ("N-Propeptide {}".format(region))
                            f_t, created = feature_type.objects.get_or_create(name='N-Cys-Collagen')
                            feat = feature.objects.filter(type=f_t,gene=g)
                            region = str(match.start('Cys') + 1)  + '..' + str(match.end('Cys'))
                            if not feat:
                                feat = feature(name='Cysteine knot', type=f_t, gene=g, region=region)
                                feat.save()
                            else:
                                feat.update(region=region)
                            NProFound = True
                            print ("N-Cys-Collagen {}".format(region))

                        if NProFound == True:
                            break
                            


                    # Finding C-Cys after collagen helix
                    reg_exprs = [   "G(.{1,3})(?P<CCys>C.{2,4}C)",
                                    "G(.{1,3})G.(?P<CCys>C.{2,4}C)",
                                    "G(.{1,3})(...){0,1}(?P<CCys>C.{1,4}C)",
                                    "G(.{1,3})(?P<CCys>CC.{1,4}C)",
                                ]   
                    for idx, reg_expr in enumerate (reg_exprs):
                        reg = re.compile (reg_expr)
                        searchstring = g.sequence[col_feat[0].end()-6:]
                        print (searchstring)
                        #quit()
                        iterator = reg.finditer(searchstring) 
                        for match in iterator:
                            f_t, created = feature_type.objects.get_or_create(name='C-Cys-Collagen')
                            feat = feature.objects.filter(type=f_t,gene=g)
                            region = str(match.start('CCys') + col_feat[0].end() - 2) + '..' + str( match.end('CCys')+ col_feat[0].end() -3)
                            if not feat:
                                feat = feature(name='Cysteine knot', type=f_t, gene=g, region=region)
                                feat.save()
                            else:
                                feat.update(region=region)
                            print ("C-Cys-Collagen {}".format(region))

                    f_t, created = feature_type.objects.get_or_create(name='N-Propeptide')
                    feat_NPro = feature.objects.filter(type=f_t,gene=g)
                    if (feat_NPro):
                        feat_NPro = feat_NPro[0]

                        # Finding N-Cys bfore collagen N-Propeptide

                        reg_exprs = ["(?P<NCys>C.{1,4}C.{1,4}C).+?((G..){4,})$",
                                    "(?P<NCys>C.{1,2}C.{5,16}?C).{2,}?((G..){4,})$",
                                    "(?P<NCys>(C.){0,1}C.{6}C).{2}((G..){4,})$", 
                                    "[^C]{20}(?P<NCys>(C)).{2}((G..){4,})$",
                                    "[^C]{20}(?P<NCys>(CC.C)).{2}((G..){4,})$",
                                    "(?P<NCys>C..CC).{2}(G..){4,}$"
                                    ]
                        print ("Searching N-Cys-Knot ... trying ...", end='')
                        searchstring = g.sequence[:feat_NPro.end()]
                        # print (searchstring)

                        found = False
                        for idx, reg_expr in enumerate (reg_exprs):
                            print ("{}".format(idx),end="")
                            reg = re.compile (reg_expr)
                            iterator = reg.finditer(searchstring) 
                            for match in iterator:
                                f_t, created = feature_type.objects.get_or_create(name='N-Cys-ProPep')
                                feat = feature.objects.filter(type=f_t,gene=g)
                                region = str(match.start('NCys') +1 ) + '..' + str( match.end('NCys'))
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
            
                
             