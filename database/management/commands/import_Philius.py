from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, feature_type, clade, project_settings


from Bio import SeqIO
from pprint import pprint
import xml.etree.ElementTree as ET
#from Bio import SearchIO

import requests, sys
import os, re

'''
 Imports Pyhllius data generate by website

'''
class Command(BaseCommand):
    help = 'Import Phylius data'

    def add_arguments(self, parser):
#        parser.add_argument(
#            '--HMMout', dest='HMMout', required=True,
#            help='The HMMER output file',
#        )
        pass


    def handle(self, *args, **options):
        
        
        tree = ET.parse(r'philius_non_cut.xml')
        root = tree.getroot()
        for child in root:
            print(child.tag, child.attrib)
            gene_name = (child.find ('fastaHeader').text[1:])
            gene_name = gene_name.split(' ')[0]
            try:
                g = gene.objects.get(name =gene_name)
            except :
                print ("Gen fehlt: {}".format(gene_name))
                exit()
            psa = (child.find ('psa'))
            # pprint (psa.get('type'))
            print ("Deleting old Philius entries from {}".format(g))
            feature.objects.filter(modeOfGeneration=feature.PHILIUS, gene=g, manually_edited=False).delete()
            
            f_t_PhType, created = feature_type.objects.get_or_create(name="PhiliusType")
            if created:
                f_t_PhType.description = "Philius type"
                f_t_PhType.color="#028cfd"
                f_t_PhType.save()
            region = "1..{}".format(len(g.sequence)+1)

            0
            if psa.get('type') == "0":
                ph_name = "Globular with Signal Peptide"
            elif psa.get('type') == "1":
                ph_name = "Globular with Signal Peptide"
            elif psa.get('type') == "2":
                ph_name = "Transmembrane"
            ph_name = psa.get('typeString')
            feat = feature(name=ph_name, type=f_t_PhType, gene=g, region=region, modeOfGeneration=feature.PHILIUS )
            feat.save()

            for segment in psa.find('segmentList'):
                segment_type = (segment.get('typeString'))
                f_t, created = feature_type.objects.get_or_create(name="ph_{}".format(segment_type))
                if created:
                    f_t.description = segment_type
                    f_t.color="#028cfd"
                    f_t.parent = f_t_PhType
                    f_t.save()
                region = "{}..{}".format(segment.get('start'),segment.get('end'))
                feat = feature(name=segment_type, type=f_t, gene=g, region=region, modeOfGeneration=feature.PHILIUS )
                
                    #       <philiusSegment id="394979" sequenceID="684072" start="1" end="19" type="0" typeString="Signal Peptide" typeConfidence="0.96">

                feat.save()
                print (feat)
            
            

