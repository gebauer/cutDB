from django.core.management.base import BaseCommand, CommandError
from Bio import SeqIO
from database.models import gene, feature, clade, transcript, feature_type

import requests, sys
import os, re

class Command(BaseCommand):

    def handle(self, *args, **options):
    
        c = clade.objects.get(identifier="cuticular_collagens")
        clades = c.get_all_children()
        for cl in clades:
            for g in cl.gene_set.all():
                try:
                    NPro_type = feature_type.objects.get(name='N-Propeptide')
                    NPro = feature.objects.get(type=NPro_type,gene=g.id)
                    Col_type =  feature_type.objects.get(name='col1_domain')
                    Col = feature.objects.get(type=Col_type,gene=g.id)
                    print ("{};{}".format(g.name,Col.start()-NPro.end()))
                except:
                    print ("{};failed".format(g.name))

