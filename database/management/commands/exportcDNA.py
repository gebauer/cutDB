import os

from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, clade, transcript
from Bio import SeqIO
from django.shortcuts import get_list_or_404, get_object_or_404
import math, io


from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

import requests, sys
from  pprint import pprint
 
class Command(BaseCommand):
    help = 'Get isoforms and make histogram'

    def add_arguments(self, parser):
        # parser.add_argument('file', nargs='+', type=str)
        pass

    def handle(self, *args, **options):
        c = clade.objects.get(identifier="collagens")
        #c = clade.objects.get(identifier="B14")
        clades = c.get_all_children()
        server = "http://parasite.wormbase.org"
        cDNAs = []
        for cl in clades:
            for gene in cl.gene_set.all():
                print ("Gene {}".format(gene.name))
                current = ''
                for trans in transcript.objects.filter(model_gene=gene).all():
                    ext = "/rest-11/sequence/id/{}?object_type=transcript;content-type:text/plain".format(trans.identifier)
                    r = requests.get(server+ext, headers={ "Accept" : "text/plain"})
                    print ("Getting transcript {} - {}".format(trans.identifier, server+ext))
                    #print (r)
                    if r.ok:
                        if len (r.text) > len (current):
                            current = r.text
                seq_r = SeqRecord(Seq(current), id=gene.name)
                cDNAs.append(seq_r)
        output = io.StringIO()
        SeqIO.write (cDNAs, "output.fasta","fasta")
        print (output.getvalue())

