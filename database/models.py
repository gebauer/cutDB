# Create your models here.
from django.db import models
from django.core.validators import RegexValidator
from tinymce import models as tinymce_models
from colorful.fields import RGBColorField
from django.utils import timezone
from django.conf import settings
from django.db.models.functions import Concat
from django.db.models import Value

from Bio import Seq, SeqRecord, SeqIO

from Bio.SeqFeature import SeqFeature, FeatureLocation, CompoundLocation
# from Bio.Alphabet import IUPAC # deprecated in BioPyhton

from subprocess import Popen, STDOUT, PIPE

from io import StringIO 

from tempfile import NamedTemporaryFile, mkstemp
import os, re
from pprint import pprint




class ExtraManager(models.Manager):

    def in_a_number_order(self, *args, **kwargs):
        qs = self.get_query_set().filter(*args, **kwargs)
        return sorted(qs, key=lambda n: (n[0], int(n[1:])))

    """QuerySet manager for Invoice class to add non-database fields.

    A @property in the model cannot be used because QuerySets (eg. return
    value from .all()) are directly tied to the database Fields -
    this does not include @property attributes."""

    def get_queryset(self):
        """Overrides the models.Manager method"""
        #qs = super(ExtraManager, self).get_queryset().annotate(sortableIdentifier=Value('identifier'))
        reg_expr = r"(?P<major>\D)(?P<minor>(?:\d)*)(?P<sub>[a-z]{0,1})"
        #re.match (reg_expr,self)
        #iterator = reg.finditer(g.sequence[:col_feat[0].start()]) 
        #                for match in iterator:
        #                    f_t, created = feature_type.objects.get_or_create(name='N-Propeptide')
        '''   qs = super(ExtraManager, self).get_queryset().annotate(sort_Idt=(Concat('identifier',Value('sd')).format())
        reg_expr = r"(?P<major>\D)(?P<minor>(?:\d)*)(?P<sub>[a-z]{0,1})"
        for entry in qs:
            print (entry.identifier)
            matches = re.match (reg_expr, entry.identifier)
            print (matches.group('major'))
            minor = matches.group('minor')
            pprint (minor)
            print (matches.group('sub'))
            if matches.group('minor') == '':
                minor = '0' 
            else:
                minor = matches.group('minor')
            if matches.group('sub') == '':
                sub = 'a'
            else:
                sub = matches.group('sub')

            print ("{major}{minor:2.0f}{sub}".format(major=matches.group('major'), minor=int(minor), sub=matches.group('sub')))
        #iterator = reg.finditer(g.sequence[:col_feat[0].start()]) 
        #                for match in iterator:
        #                    f_t, created = feature_type.objects.get_or_create(name='N-Propeptide')

            entry['sortID'] = 'test
        '''
        qs = super(ExtraManager, self).get_queryset()
        return qs


class transcript(models.Model):
    identifier = models.CharField('Transcript identifier',max_length=31, unique=True)
    description = tinymce_models.HTMLField( blank=True)
    model_gene = models.ForeignKey('gene', null=True,related_name='model_transcript',on_delete=models.CASCADE) 
    chromosome = models.CharField('Chromosome',max_length=10, unique=False)
    region = models.CharField (max_length=10000, validators=[
        RegexValidator(
        
                regex=r'((\d+\.\.\d+),){0,}(\d+\.\.\d+)',
                message='Please enter the region in the format 12..34,24..45',
                code='invalidRegion'
                )])



class clade(models.Model):
    #objects = models.Manager() # The default manager.
    objects = ExtraManager()
    #objects = 
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True,blank=True)
    identifier = models.CharField('Sub-Identifier',max_length=31, unique=True)
    regExpr = models.CharField('Regular expression to identify this clade without the /s',max_length=100, blank=True)
    description = tinymce_models.HTMLField( blank=True)
    alignment = models.TextField ('Calculated Alginment for all alignment members', blank=True)
    alignment_date = models.TextField ('last calculated alignment', default=timezone.now )
    model_gene = models.ForeignKey('gene', null=True, blank=True,related_name='model_clade',on_delete=models.SET_NULL) 


    
    class Meta:
        pass
        ordering = ['identifier']
     
    def __str__(self):
        return self.get_fullname()
    
    def get_fullname (self):
        return self.identifier

    def get_gene_sequences (self, recursive=False):
        genes = []
        clades = []
        if recursive == True:
            clades = self.get_all_children(True)
        else:
            clades.append (self)   
  
        for clade in clades:
            for gene in clade.gene_set.all():
                single = gene.getSeqRecord()
                genes.append(single)
        return (genes)

    def get_gene_names (self, recursive=True):
        # get all Names fomr genes in this clade...
        genes = []
        clades = []
        if recursive == True:
            clades = self.get_all_children(True)
        else:
            clades.append (self)   
        for clade in clades:
            for gene in clade.gene_set.all():
                single = gene.name
                genes.append(single)

        return (genes)

    def has_children(self):
        return (clade.objects.filter(parent=self).exists())

    def get_all_children(self, include_self=True):
        r = []
        if include_self:
            r.append(self)
        for c in clade.objects.filter(parent=self).order_by('identifier'):
            _r = c.get_all_children(include_self=True)
            if 0 < len(_r):
                r.extend(_r)
        return r

    def get_all_children_ids(self, include_self=True):
        r = []
        for id in self.get_all_children (include_self):
            r.append (id.identifier)
        return r
    
    def get_model_gene (self):
        # Simple way of determining the model gene for this clade.
        if self.model_gene != None:
            if self.model_gene.clade.filter (identifier__in=self.get_all_children_ids(True)).exists():
                return (self.model_gene)
            else:
                return ("ERROR")
        else:
            for clade in self.get_all_children(True):
                for gene in clade.gene_set.all():
                    return (gene)


    def gene_count (self, recursive=False):
        if recursive == True:
            count = 0
            clades = self.get_all_children(True)
            for clade in clades:
                count += clade.gene_count(False)
            return (count)
        else:
            return (self.gene_set.count ())
    
    def gene_all_count (self):
        return (self.gene_count (True))

    def get_alignment (self, recursive=False):
  
        #myfile  = open(r"C:\Users\gebauer\AppData\Local\Temp\temp2.txt", 'w')
        #SeqIO.write (self.get_gene_sequences(recursive), myfile,"fasta")
    
        myfile = StringIO()
        SeqIO.write (self.get_gene_sequences(recursive), myfile,"fasta")
        #print ("===============================")
        #print ("sequences 2")
       # print ( self.get_gene_sequences(recursive))

       
        if self.gene_count (recursive) > 1:

            matrix_handle,matrix_name = mkstemp()
            handle = os.fdopen (matrix_handle,'r+')

            # print ("matrix name",matrix_name)

            proc = Popen([settings.CLUSTALO_BIN, '--infile=-', '--full', '--percent-id','--distmat-out='+matrix_name, '--force'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
          #  proc = Popen([clustalo.exe', '--infile=-', '--full', '--percent-id','--distmat-out='+matrix_name, '--force'], stdout=PIPE, stdin=PIPE, stderr=PIPE, executable='"c:\Program Files (x86)\clustal-omega-1.2.2-win64\"' )
            stdout, stderr = proc.communicate(input = str.encode(myfile.getvalue()))
            
            #handle.close()
            #handle = open (matrix_handle,'r')
            #print (matrix)
            #+myfile.getvalue())
            #file = open(matrix_name, 'r')
            identity_matrix = handle.read()
            os.close (matrix_handle)
            os.remove(matrix_name)
            # print (identity_matrix)
            identities = {}
            ident_array =[]
            for line in identity_matrix.splitlines()[1:]:
                identities[line.split()[0]] =  list(map(float, line.split()[1:]))
                ident_array.append ([line.split()[0],list(map(float, line.split()[1:]))])
#                ident_array.append (list(map(float, line.split()[1:])))
            print (ident_array)


            #print ("alignment")
            #print (stdout)
            #print (stderr)
            return ({'alignment' : stdout, 'identities' : ident_array })
        else:
            return ({'alignment' : str.encode(myfile.getvalue()), 'identities' :'', 'ident_array':'' })
        

class project_settings (models.Model):
    s_key = models.CharField('Setting key',max_length=40, unique=True)
    s_value  = models.CharField('Setting value',max_length=256)

class gene(models.Model):
    gene_id = models.CharField('Gene id in entrez',max_length=20)
    wormbase_id = models.CharField(max_length=100, blank=True)
    prot_id  = models.CharField('UniProt Id', max_length=20, blank=True)
    last_changed = models.DateTimeField('last changed', default=timezone.now )
    sequence = models.CharField('Amino acid sequence',max_length=5000)
    name = models.CharField('My official gene name',max_length=40, unique=True)
    alias = models.CharField('Aliases',max_length=100, blank=True)
    clade = models.ManyToManyField(clade, null=True, blank=True) 
    
    description = tinymce_models.HTMLField( blank=True)
    
    class Meta:
        pass
        ordering = ['name']
    
    def __str__(self):
        return ("{} ({} / {})".format(self.name,self.gene_id, self.prot_id))

    def getSeqRecord (self):
        my_SeqRec = SeqRecord.SeqRecord (Seq.Seq(self.sequence, IUPAC.protein))
        my_SeqRec.id = self.name
        
        #my_SeqRec.id = self.gene_id
        my_SeqRec.description = self.description
        my_SeqRec.name = self.name
        #my_SeqRec.description = '' # Should we include a text here?

        for feature in self.feature_set.all():
            compound = []
            if len(feature.region_to_array())> 1:
                for element in feature.region_to_array():
                    

                    compound.append (FeatureLocation (int(element[0])-1,int(element[1])))
                location = CompoundLocation(compound)
            else:
                location = FeatureLocation (int(feature.region_to_array()[0][0])-1,int(feature.region_to_array()[0][1]))
            #print (self.name)
            #print ("location", location)
            my_feature = SeqFeature (location, type=feature.type.name,strand=+1,qualifiers={'description':feature.name})
            my_SeqRec.features.append(my_feature)
        

        return my_SeqRec




class feature_type(models.Model):    
    name = models.CharField(max_length=15,  unique=True)
    description = tinymce_models.HTMLField(blank=True)
    parent = models.ForeignKey('self',on_delete=models.CASCADE, null=True,blank=True)
    color = RGBColorField(default="#FFC300")
    style = models.CharField(max_length=50, blank=True)
    domain_list = models.BooleanField (default=True)
    pfam_id = models.CharField(max_length=20,  null=True, blank=True)
    
    def __str__(self):
        return self.name

    def get_all_children(self, include_self=True):
        r = []
        if include_self:
            r.append(self)
        for c in feature_type.objects.filter(parent=self):
            _r = c.get_all_children(include_self=True)
            if 0 < len(_r):
                r.extend(_r)
        return r
    
    def get_unique(self):
        children = self.feature_set.all().order_by('gene').values('gene').distinct()
        unique_list = []
        for value in children:
            unique_list.append(value['gene'])

        children = gene.objects.filter(pk__in=unique_list)
        return (children)
        pass


    
class feature(models.Model):
    type = models.ForeignKey (feature_type,on_delete=models.CASCADE)
    gene = models.ForeignKey (gene,on_delete=models.CASCADE)
    name = models.CharField(max_length=50,default = 'Col1 domain')
    description = tinymce_models.HTMLField(blank=True)
    manually_edited =models.BooleanField(default=False)
    PFAM = 'PF'
    SIGNALP = 'SP'
    REGEXP = 'RX'
    MANUAL = 'MN'
    PHILIUS = 'PI'
    algorithms = (
        (PFAM, 'PFAM'),
        (SIGNALP, 'SignalP'),
        (REGEXP, 'Regular Expressions'),
        (PHILIUS, 'Philius Webserver'),
        (MANUAL, 'manual'),
    )
    modeOfGeneration = models.CharField(max_length=2, choices=algorithms, default=REGEXP,) 
    region = models.CharField (max_length=100, validators=[
            RegexValidator(
            
                    regex=r'((\d+\.\.\d+),){0,}(\d+\.\.\d+)',
                    message='Please enter the region in the format 12..34,24..45',
                    code='invalidRegion'
                    )])
    
    def __str__(self):
        return str(self.type) +" ("+self.region+")" 
    
    def region_to_array(self):
        result =[]
        array = str(self.region).split(',')
        for element in array:
            xy = element.split('..')
            # print (xy)
            result.append(xy)
        return (result)            
        
    def xy_set (self):
        region_set =  ""
        for element in self.region_to_array():
            region_set += "{{x:{},y:{},id:{:1.0f}}},".format(element[0],element[1],self.id)
        return (region_set.rstrip(','))
        
    def start (self):
        return (int(self.region_to_array()[0][0]))
    
    def end (self):
        return (int(self.region_to_array()[-1][1]))

    def get_sequence (self):
        return (self.gene.sequence[self.start()-1:self.end()])
    
#    def isCutCol (self):
#        if self.algorithms in [REGEXP = 'RX'   MANUAL = 'MN']
    
