from django.core.management.base import BaseCommand, CommandError
from Bio import SeqIO
from database.models import gene, feature, clade, transcript

import requests, sys
import os, re

class Command(BaseCommand):
    help = 'Count how many hyp could be possible'

    def add_arguments(self, parser):
          pass
          #parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        count_yP = 0
        count_yX = 0
        count_yPP = 0


        c = clade.objects.get(identifier="collagens")
        clades = c.get_all_children()
        cDNAs = []
        for cl in clades:

            for g in cl.gene_set.all():
                count_yP = 0
                count_yX = 0  
                count_yPP = 0
                seq = g.sequence
                reg_expr = "((?:G..){5,})"  # Eveything with more than 4 triplets is a collagen...
                reg = re.compile (reg_expr)
                iterator = reg.finditer(seq) 
                result = []
                print (seq)
                for match in iterator:
                    
                    s = match.group(0)
                    print ('')
                    print (s)
                    print ('  ', end="")
                    for i in range (2, len(s), 3):
                        print (s[i] +  '  ',end="")
                        if s[i] == 'P':
                            count_yP += 1
                        if s [i-1:i+1] == 'PP':
                            count_yPP +=1
                        
                        count_yX += 1
            
                print ("P on X: {}  |  P on Y {}  | triples {}".format (count_yX, count_yP,))
            
            exit() 
            print  (options['file'][1])  
            try:
                f = open(options['file'][1],'r')
            except ValueError:
                print ("File not found!")
            else:
                for record in SeqIO.parse(f, "genbank"):
                    print (record.id)
                    reg_expr = "((?:G..){5,})"  # Eveything with more than 4 triplets is a collagen...
                    reg = re.compile (reg_expr)
                    g = gene (name=record.name, sequence=record.seq, gene_id=record.id)
                    seq = g.sequence
                    print (seq)
                    iterator = reg.finditer(str(seq))
                    result = []
                    for match in iterator:
                        
                        s = match.group(0)
                        print ('')
                        print (s)
                        print ('  ', end="")
                        for i in range (2, len(s), 3):
                            print (s[i] +  '  ',end="")
                            if s[i] == 'P':
                                count_yP += 1
                            if s [i-1:i+1] == 'PP':
                                count_yPP +=1
                            
                            count_yX += 1
            
            print ("P on X: {}  |  P on Y {}  | triples {}".format (count_yX, count_yP,))

    
