from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, feature_type, clade, project_settings


from Bio import SeqIO

import requests, sys
import os, re, sys

class Command(BaseCommand):
    help = 'Check if genes are Pseudogenes'

    def add_arguments(self, parser):
          #parser.add_argument('file', nargs='+', type=str)
          pass

    def handle(self, *args, **options):
        for g in gene.objects.all():

            print ("check {}".format(g.name),end='')
            sys.stdout.flush()
            server = "http://parasite.wormbase.org"
            ext = "/rest-10/lookup/id/{}?expand=1".format(g.wormbase_id) 
            if (len (g.wormbase_id) < 5):
                print ("\r{} has no wormbase id".format(g.name))
                quit()

            r = requests.get(server+ext, headers={ "Content-Type" : "application/json", "Accept" : ""})
            if not r.ok:
                r.raise_for_status()
                print ("\r{} could not be verified".format(g.name))
                quit()
            decoded = r.json()
            if decoded['biotype'] != "protein_coding":
                print ("\r{} is not protein_coding".format(g.name))
                quit()
            print ("\r{} is {} ".format(g.name,decoded['biotype']))

        print ("... all finished")
                
