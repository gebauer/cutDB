from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, feature_type, clade, project_settings


from Bio import SeqIO
from pprint import pprint
#from Bio import SearchIO

import requests, sys
import os, re

'''
 Imports SignalP features

 You can create the necessary output file by this command:
 
 signalp -t euk -f short ~/xtal/non-cuticular.fasta  >~/signalp.out 
 
 signalp -t euk -s notm -f summary ~/xtal/root.fasta  >~/signalp.out 
 (on a Linux system)

'''
class Command(BaseCommand):
    help = 'Import features from SignalP'

    def add_arguments(self, parser):
#        parser.add_argument(
#            '--HMMout', dest='HMMout', required=True,
#            help='The HMMER output file',
#        )
        pass


    def handle(self, *args, **options):
        SignalP_IN = r'X:\signalp.out'
        self.stdout.write("Opening file {}".format(SignalP_IN))
        handle = open (SignalP_IN,'r')
        #self.stdout.write (handle.readline())
        reg_expr = r"^Name=(.+)\sSP='YES'\sCleavage\ssite\sbetween\spos\.\s(\d+)\sand\s(\d+):"
        reg = re.compile (reg_expr)
        for line in handle.readlines():
            iterator = reg.finditer(line) 
            #self.stdout.write (line)
            for match in iterator:
                gene_name =  match[1]
                sig_end = match[2]
                try:
                    g = gene.objects.get(name =gene_name)
                except :
                    print ("Gen fehlt: {}".format(gene_name))
                    exit()
                print ("Deleting old SignalP entrie from {}".format(g))
                feature.objects.filter(modeOfGeneration=feature.SIGNALP, gene=g, manually_edited=False).delete()
                f_t, created = feature_type.objects.get_or_create(name="SignalP")
                if created:
                    f_t.description = "SignalP 4.1 prediction"
                    f_t.color="#028cfd"
                    f_t.save()
                print ("save feature")
                region = "1..{}".format(sig_end)
                feat = feature(name="SignalP", type=f_t, gene=g, region=region, modeOfGeneration=feature.SIGNALP )
                print ("Save "+str(feat))
                feat.save()