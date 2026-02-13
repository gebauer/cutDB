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

   #     c = clade.objects.get(identifier="B14")
        clades = c.get_all_children()
        cDNAs = []
        fh = open("Lys.csv",'w')
        stats ={'A':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0, 'K':0, 'L':0, 'M':0, 'N':0, 'P':0, 'Q':0, 'R':0, 'S':0, 'T':0, 'V':0, 'W':0, 'Y':0  }
        statsX ={'A':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0, 'K':0, 'L':0, 'M':0, 'N':0, 'P':0, 'Q':0, 'R':0, 'S':0, 'T':0, 'V':0, 'W':0, 'Y':0  }

        fh.write ("Gene;Clade;#Y;{};#X;{}\n".format(";".join(sorted(stats.keys())),";".join(sorted(statsX.keys())))  )

        for cl in clades:

            for g in cl.gene_set.all():
                count_yX = 0  
                count_xX = 0  
                count_yPP = 0
                stats ={'A':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0, 'K':0, 'L':0, 'M':0, 'N':0, 'P':0, 'Q':0, 'R':0, 'S':0, 'T':0, 'V':0, 'W':0, 'Y':0  }
                statsX ={'A':0, 'C':0, 'D':0, 'E':0, 'F':0, 'G':0, 'H':0, 'I':0, 'K':0, 'L':0, 'M':0, 'N':0, 'P':0, 'Q':0, 'R':0, 'S':0, 'T':0, 'V':0, 'W':0, 'Y':0  }
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
                        if s[i] in stats:
                            stats[s[i]] +=1
                        else:
                            stats[s[i]] =0

                        if s [i-1:i+1] == 'PP':
                            count_yPP +=1
                        
                        count_yX += 1
                    for i in range (1, len(s), 3):
                        print (s[i] +  '  ',end="")
                        if s[i] in stats:
                            statsX[s[i]] +=1
                        else:
                            statsX[s[i]] =0
                        count_xX += 1
            
                print ("\nY-Positions: {}  |  L on Y {}  | GPP triples {}\n".format (count_yX, count_yP,count_yPP))
                print (g.name)
                print ()
             #   print ("{}".format(';'.join(stats.values())))
                fh.write ("{};{};{};{};{};{}\n".format (g.name, cl.identifier, count_yX, ';'.join(str(stats[x]) for x in sorted(stats)), count_xX, ';'.join(str(statsX[x]) for x in sorted(statsX))))

        fh.close()
            
 