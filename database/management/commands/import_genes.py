
import os

from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, clade
from Bio import SeqIO

import requests, sys
 
class Command(BaseCommand):
    help = 'Import genes from an external file'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            f = open(options['file'][1],'r')
        except ValueError:
            print ("File not found!")
        else:
            for record in SeqIO.parse(f, "genbank"):
                print (record.id)
                g = gene (name=record.name, sequence=record.seq, gene_id=record.id)
                server = "http://parasite.wormbase.org"
                ext = "/rest-9/xrefs/symbol/Caenorhabditis_elegans_prjna13758/"+str(g.gene_id).split('.')[0]+"?"
                r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})
                if r.ok:
                    decoded = r.json()
                    for match in decoded:
                        if ('type' in match and match['type'] == "gene"):
                            g.wormbase_id =match['id']
                            ext2 = "/rest-9/xrefs/id/"+g.wormbase_id
                            r2 = requests.get(server+ext2, headers={ "Content-Type" : "application/json"})
                            decoded2 = r2.json()
                            for match2 in decoded2:
                                if ('dbname' in match2 and match2['dbname'] == "Uniprot_gn"):
                                    g.prot_id = match2['primary_id']
                g.save()
                                    

