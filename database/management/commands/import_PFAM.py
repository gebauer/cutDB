from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, feature_type, clade, project_settings


from Bio import SeqIO
from pprint import pprint
from Bio import SearchIO

import requests, sys
import os, re

'''
 Imports PFAM  predictions into cutDB

 You can create the necessary output file by this command:
 hmmscan --cut_ga -o txtout.txt /mnt/g/PFAM/Pfam-A.hmm /mnt/d/CodingProjects/LocalDB/sfT_6239_results.2.fa

'''
class Command(BaseCommand):
    help = 'Count how many hyp could be possible'

    def add_arguments(self, parser):
#        parser.add_argument(
#            '--HMMout', dest='HMMout', required=True,
#            help='The HMMER output file',
#        )
        pass


    def handle(self, *args, **options):
        HMMout = r'D:\Downloads\hmmer3.0_windows\txtout.txt'
        self.stdout.write("Opening file {}".format(HMMout))
        handle = open (HMMout,'r')
        QueryRslt  = SearchIO.parse(handle,'hmmer3-text')
        for hit in QueryRslt:
            print (hit.id)
            try:
                g = gene.objects.get(prot_id=hit.id)
            except :
                print ("Uniprot fehlt: {}".format(hit.id))
                exit()
            print ("Deleting old PFAM entries from {}".format(g))
            feature.objects.filter(modeOfGeneration=feature.PFAM, gene=g, manually_edited=False).delete()
            for HSP in hit:
                print (HSP.id)
                f_t, created = feature_type.objects.get_or_create(name=HSP.id)
                if created:
                    f_t.description = HSP.description
                    f_t.color="#C70039"
                    f_t.save()

                for HSPF in HSP:
                    print ("save feature")
                    region = "{}..{}".format(HSPF.query_start, HSPF.query_end)
                    feat = feature(name=HSP.id, type=f_t, gene=g, region=region, modeOfGeneration=feature.PFAM )
                    print ("Save "+str(feat))
                    feat.save()
                     

        quit ()

        exit()
        f_t1 = feature_type.objects.get (name='col1_domain')
        for g in gene.objects.all():
            if g.name in ['COL121',]:
                print ("====")
                print (f_t1)
                col_feat = g.feature_set.filter(type = f_t1)
                print (col_feat)
                if col_feat:
                    reg_expr = "(?P<NPro>(?:G..){7,}).{5,14}(?P<Cys>C.{2,5}C).{1,3}G"
                    # reg_expr = "(?P<NPro>(?:G..){7,}).{5,14}(?P<Cys>C*.{2,5}C).{1,3}G" 

                    reg_expr = "(?P<NPro>(?:G..){7,}).{5,14}(?P<Cys>C.{2,5}C).{1,5}G"
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
                        f_t, created = feature_type.objects.get_or_create(name='N-Cys-Collagen')
                        feat = feature.objects.filter(type=f_t,gene=g)
                        region = str(match.start('Cys') + 1)  + '..' + str(match.end('Cys'))
                        if not feat:
                            feat = feature(name='Cysteine knot', type=f_t, gene=g, region=region)
                            feat.save()
                        else:
                            feat.update(region=region)


            
             