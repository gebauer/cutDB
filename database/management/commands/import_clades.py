from django.core.management.base import BaseCommand, CommandError
from database.models import gene, feature, clade

import os

class Command(BaseCommand):
    help = 'Import clades from an external file'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=str)

    def handle(self, *args, **options):
        print (options['file'][1])
        try:
            f = open(options['file'][1],'r')
        except ValueError:
            print ("File not found!")
            print (ValueError)
        else:
            for line in f:
                values = line.split(';') 
                print (values[1])
                if (values[1] != ""):
                    parent_clade = clade.objects.get(identifier=values[1])
                else:
                    parent_clade = None
                c, created = clade.objects.get_or_create(identifier=values[0])
                print (c)
                c.parent = parent_clade
                c.regExpr = values[2]
                c.description = values[3]
                print (c)
                c.save()

