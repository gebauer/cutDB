import os

from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, clade, transcript
from Bio import SeqIO
from django.shortcuts import get_list_or_404, get_object_or_404
import math

import requests, sys
from  pprint import pprint
 
class Command(BaseCommand):
    help = 'Get isoforms and make histogram'

    def add_arguments(self, parser):
        # parser.add_argument('file', nargs='+', type=str)
        pass

    def handle(self, *args, **options):
        c = clade.objects.get(identifier="collagens")
        clades = c.get_all_children()
        exons= {}
        for cl in clades:
            for gene in cl.gene_set.all():
                print ("Deleting existing transcript files from {}".format(gene))
                transcript.objects.filter(model_gene=gene).delete()

                server = "http://parasite.wormbase.org"
                ext = "/rest-10/lookup/id/{}?content-type=application/json;expand=1".format(gene.wormbase_id)

                r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
                if r.ok:
                    decoded = r.json()
                    for single_transcript in decoded["Transcript"]:
                        region = ''
                        for exon in single_transcript['Exon']:
                            length = int (math.fabs(exon['end']-exon['start'])+1)
                            #pprint ("{}".format(length))
                            if length in exons.keys():
                                exons [length] = exons [length]+1
                            else:
                                exons [length] = 1
                            region += '{}..{},'.format (exon['start'], exon['end'])
                        print (region[:-1])
                        transcript_object = transcript(identifier=single_transcript['id'], model_gene=gene, region=region)
                        transcript_object.save()

                    '''for match in decoded:
                        if ('type' in match and match['type'] == "gene"):
                            g.wormbase_id =match['id']
                            ext2 = "/rest-9/xrefs/id/"+g.wormbase_id
                            r2 = requests.get(server+ext2, headers={ "Content-Type" : "application/json"})
                            decoded2 = r2.json()
                            for match2 in decoded2:
                                if ('dbname' in match2 and match2['dbname'] == "Uniprot_gn"):
                                    g.prot_id = match2['primary_id']
            '''
                    #print('\r\n'.join('{};{}'.format(key, value) for key, value in exons.items()))
                    #exit()

