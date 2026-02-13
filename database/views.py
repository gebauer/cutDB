from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


from .models import gene, feature, clade, feature_type, project_settings

from django.db.models import Q

from Bio import SeqIO

from django.db import connection
from django.conf import settings
import os
from datetime import datetime

import re
import json
from io import StringIO

def index(request):
    template = loader.get_template('database/index.html')
    free_genes = gene.objects.filter(clade__isnull=True).count()
    gene.objects.filter()
    noncuticular = gene.objects.filter(clade__identifier='non-cuticular').count()
    #print(get_object_or_404(project_settings, s_key="db_version").s_value)
    # "Last updated" date: MySQL has information_schema; SQLite uses db file mtime
    if connection.vendor == 'sqlite':
        db_path = settings.DATABASES['default']['NAME']
        if os.path.isfile(db_path):
            date = datetime.fromtimestamp(os.path.getmtime(db_path))
        else:
            date = None
    else:
        cursor = connection.cursor()
        sql = '''SELECT UPDATE_TIME
                FROM information_schema.tables
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME LIKE 'database%%'
                ORDER BY UPDATE_TIME DESC'''
        cursor.execute(sql, [settings.DATABASES['default']['NAME']])
        row = cursor.fetchone()
        date = row[0] if row else None

    context = {
        'statistics': {
            'genes_all' : gene.objects.all().count(),
            'genes_classified' : gene.objects.filter(clade__isnull=False).exclude(clade__identifier='non-cuticular').count(),
            'genes_non_cut' : gene.objects.filter(clade__identifier='non-cuticular').exclude(clade__identifier='no_collagen').count(),
            'genes_not_collagen' : gene.objects.filter(clade__identifier='no_collagen').count(),
            'genes_non_classified' : gene.objects.filter(clade__isnull=True).count(),
        },
        'version': {get_object_or_404(project_settings, s_key="db_version").s_value},
        'date' : date,
    }
    return HttpResponse(template.render(context, request))

def genes(request):
    all_genes = gene.objects.all()
    template = loader.get_template('database/genes.html')
    context = {
        'all_genes': all_genes,
    }
    return HttpResponse(template.render(context, request))
    

def gene_detail(request, gene_name):
    g = get_object_or_404(gene, name=gene_name)
    transcript = g.model_transcript.all().count()
    transcript_url = "http://parasite.wormbase.org/Caenorhabditis_elegans_prjna13758/Gene/Splice?db=core;g={WBGene}".format (WBGene=g.wormbase_id)

    return render(request, 'database/gene_detail.html', {'gene': g, 'transcript': transcript,'transcript_url':transcript_url})


def clades(request):
    
    def again (request2):
        tree2=''
        for clade1 in request2:
            tree2 += "<li class='folder'><a href='{url}'>{name} ({count}) </a>\n".format(url=reverse('clade_info',args=[clade1.identifier]), 
                                                                                         name=clade1.identifier, 
                                                                                         count=len(clade1.get_gene_names())
                                                                                        )
            if (clade1.has_children) or (count (clade1.gene_set.all()) > 0):
                tree2 += "<ul>\n"
                if clade1.has_children:
                    tree2 += again (clade.objects.filter(parent=clade1.id))
                for gene1 in clade1.gene_set.all():
                    tree2 += "<li><a href='{url}'>{gene}</a>\n".format(url=reverse('gene_info',args=[gene1.name]), gene=gene1.name)
                tree2 += "</ul>\n"
        return (tree2)
    
    tree = "<div id='tree'><ul>\n"
    tree += again (clade.objects.exclude(parent_id__isnull=False))
    tree += "<li class='folder'>without cluster assignment\n<ul>\n"
    for gene1 in gene.objects.filter(clade__isnull=True):
        tree += "<li><a href='{url}'>{name}</a>\n".format(url=reverse('gene_info',args=[gene1.name]), gene=gene1.name)
    tree += "</ul>\n"

    tree += "</ul></div>"

    template = loader.get_template('database/clades.html')
    context = {
        'tree' : tree
 

    }
    return HttpResponse(template.render(context, request))


def clade_detail(request, clade_identifier):
    c = get_object_or_404(clade, identifier=clade_identifier)
    text = ''
    recursive = request.GET.get('recursive', False)
    if recursive == 'True':
        recursive = True
    else:
        recursive = False
    clades = []
    if recursive == True:
        clades = c.get_all_children()
    else:
        clades.append (c)

    clades_noParents = []
    if recursive == True:
        for c2 in c.get_all_children():
            if not c2.has_children ():
                clades_noParents.append (c2)
    else:
        clades_noParents.append (c)

    align = c.get_alignment(recursive)
    table_data = []
    #print ("2")
    for cl in clades:
        for gene in cl.gene_set.all():
            dat = {}

            dat['id'] = "<a href='"+reverse('gene_info', args=(gene.name,))+"'>"+gene.name+"</a>"
            f_t = feature_type.objects.get(name='N-Propeptide')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature", feat)
                dat['NPro'] = gene.sequence[feat.start()-1:feat.end()].replace('G','<span class="mark_char_G">G</span>')
            except ObjectDoesNotExist:
                pass

            f_t = feature_type.objects.get(name='N-Cys-Collagen')
            KnotCAddition = 1
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat)
                dat ['NColCys'] = gene.sequence[feat.start()-1:feat.end()+KnotCAddition].replace('C','<span class="mark_char_C">C</span>')
            except ObjectDoesNotExist:
                pass

            f_t = feature_type.objects.get(name='C-Cys-Collagen')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat)
                dat ['CColCys'] = gene.sequence[feat.start()-1:feat.end()+KnotCAddition].replace('C','<span class="mark_char_C">C</span>')
            except ObjectDoesNotExist:
                pass

            f_t = feature_type.objects.get(name='N-Cys-ProPep')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat)
                dat ['NProCys'] = gene.sequence[feat.start()-1:feat.end()+KnotCAddition].replace('C','<span class="mark_char_C">C</span>')
            except ObjectDoesNotExist:
                pass

            f_t = feature_type.objects.get(name='C-Cys-ProPep')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat)
                dat ['CProCys'] = gene.sequence[feat.start()-1:feat.end()+KnotCAddition].replace('C','<span class="mark_char_C">C</span>')
            except ObjectDoesNotExist:
                pass

            f_t = feature_type.objects.get(name='col1_domain')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat.region_to_array())
                region = feat.region_to_array()
                total = 0
                dat ['start_col'] = feat.start()
                for i in range (0, len(region)):
                    #print ("reg",region[i])
                    #print ('str', str(i))
                    #print (s,region[i][1] - region[i][0] )
                    total += int(region[i][1]) - int(region[i][0])+1
                    dat['Col%s' % (i+1)] = int(region[i][1]) - int(region[i][0])+1
                    #print (i)
                    if i > 0:
                        dat['NC%s' % (i)] = int(region[i][0]) - int(region[i-1][1])-1
                        total += int(region[i][0]) - int(region[i-1][1])-1

                dat ['total'] = total
                #dat ['NProCys'] = gene.sequence[feat.start()-1:feat.end()].replace('C','<span class="mark_char_C">C</span>')
            except ObjectDoesNotExist:
                pass
            f_t = feature_type.objects.get(name='PhiliusType')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat)
                dat ['PhiliusType'] = feat.name
            except ObjectDoesNotExist:
                dat ['PhiliusType'] = ''

            f_t = feature_type.objects.get(name='predictedFurin')
            try:
                #print ("Feature",feat)
                s = ''
                for furin in feature.objects.filter(type=f_t,gene=gene.id):
                    s =  "{}{}, ".format(s, furin.end())
                dat ['furinsite'] = s[:-2]
            except ObjectDoesNotExist:
                dat ['furinsite'] = 0

            f_t = feature_type.objects.get(name='RGD_motif')
            try:
                #print ("Feature",feat)
                s = ''
                for RGD in feature.objects.filter(type=f_t,gene=gene.id):
                    s =  "{}{}, ".format(s, RGD.end())
                dat ['RGDsite'] = s[:-2]
            except ObjectDoesNotExist:
                dat ['RGDsite'] = 0

            dat ['SignalP'] = 'n.a.'

            f_t = feature_type.objects.get(name='ph_SigPep')
            try:
                feat = feature.objects.get(type=f_t,gene=gene.id)
                #print ("Feature",feat)
                dat ['SignalP'] = feat.region
            except ObjectDoesNotExist:
                pass
            f_t = feature_type.objects.get(name='ph_Transmem')
            # print (gene.id)
            try:
                s = ''
                for membrane in feature.objects.filter(type=f_t,gene=gene.id):
                    s =  "{}{}, ".format(s, membrane.region)
                if s != '':
                    dat ['SignalP'] = s[:-2]

            except ObjectDoesNotExist:
                pass

            dat['Protein_Length'] = len(gene.sequence)
            if ('start_col' in dat):
                dat['Length_CT'] = len(gene.sequence)-(dat['start_col']+dat['total'])
                
            dat ['clade'] = "<a href='"+reverse('clade_info', args=(str(gene.clade.all()[0]),))+"'>"+ str(gene.clade.all()[0]) +"</a>"
            dat ['WBGene'] = "<a href='https://wormbase.org/species/c_elegans/gene/{WBGene}'>{WBGene}</a>".format (WBGene=gene.wormbase_id)
            dat ['transcript'] = "<a href='http://parasite.wormbase.org/Caenorhabditis_elegans_prjna13758/Gene/Splice?db=core;g={WBGene}'>{count}</a>".format (count=gene.model_transcript.all().count(), WBGene=gene.wormbase_id)
            
            
            table_data.append(dat)
            #print (gene)
    #print ("3")

    '''
    data: [{
        id: '',
        clade: '',
        SignalP:'',
        NProCys: '',
        NPro: '',
        CProCys: '',
        NColCys: '',
        Col1: '',
        NC1: '',
        Col2: '',
        NC2: '',
        Col3: '',
        NC3: '',
        Col4: '',
        total: '',
        CColCys: '',
        WBGene: '',
        Length_CT: '',
    }]
    '''
    # Decode alignment bytes for template; use UTF-8 (unicode_escape corrupts alignment text)
    align_bytes = align['alignment']
    alignment_str = align_bytes.decode('utf-8', errors='replace') if isinstance(align_bytes, bytes) else align_bytes
    context = {
        'clade': c,
        'recursive' : recursive,
        'clades' : clades,
        'alignment' : alignment_str,
        'alignment_json' : json.dumps(alignment_str),  # safe for embedding in JS (no backtick/${ issues)
        'identity_items' : align['identities'],
        'gene_count' : c.gene_count(recursive),
        'table_data' : json.dumps(table_data),
        'clades_noParents' : clades_noParents,
 
    }
    return render(request, 'database/clade_detail.html', context)


@login_required
def gene_add_clade  (request):
    #print ("add clade")
    if request.method == 'POST':
        gene_name = request.POST.get('gene_name')
        clade_id = request.POST.get('clade_id')
        matches = json.loads(request.POST.get('matches'))
        active_gene = get_object_or_404(gene, name=gene_name)
        active_clade = get_object_or_404(clade, identifier=clade_id)
        active_gene.clade.add (active_clade)
        # active_gene.save()
        #print ("matches:",matches)
        for match in matches:
            f_t, created = feature_type.objects.get_or_create(name='col1_domain')
            #print ("match:", match)
            #print (match['region'])
            feat = feature.objects.filter(type=f_t,gene=active_gene )
            if not feat:
                feat = feature(name='Col1-domain', type=f_t, gene=active_gene, region=match['region'])
                feat.save()
            else:
                feat.update(region=match['region'])

            

        #print (">"+active_gene.sequence)
        return HttpResponse(
            json.dumps('Succefully added'),
            content_type="application/json"
        )
    else:
        #print ("!")
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def clade_export_ajax (request, clade_identifier, format, rec):

    #print ("gotIt")
    if rec == 'True':
        recursive = True
    else:
        recursive = False
    

    myfile = StringIO()
    active_clade = get_object_or_404(clade, identifier=clade_identifier)
    genes = []

    
    if format == "genbank":
        SeqIO.write (active_clade.get_gene_sequences(recursive), myfile,"genbank")
        response = HttpResponse(myfile.getvalue(), content_type='chemical/x-genbank')
        response['Content-Disposition'] = 'attachment; filename="'+active_clade.identifier+'.gb"'
    else:   # defaulting to fasta
        SeqIO.write (active_clade.get_gene_sequences(recursive), myfile,"fasta")
        response = HttpResponse(myfile.getvalue(), content_type='chemical/seq-aa-fasta')
        response['Content-Disposition'] = 'attachment; filename="'+active_clade.identifier+'.fasta"'

    response['Content-Transfer'] = "Encoding: binary"
    response['Content-Length'] = myfile.tell()
    return response

def gene_export_ajax (request, gene_name, format):
    #print ("hallo")
    myfile = StringIO()
    #myfile.write('>Fasta\nMYPROTEINSEQUENCE')
    active_gene = get_object_or_404(gene, name=gene_name)
    test = active_gene.getSeqRecord()
    if format == "genbank":
        SeqIO.write (test, myfile,"genbank")
        response = HttpResponse(myfile.getvalue(), content_type='chemical/x-genbank')
        response['Content-Disposition'] = 'attachment; filename="'+gene_name+'.gb"'
    else:
        SeqIO.write (test, myfile,"fasta")
        response = HttpResponse(myfile.getvalue(), content_type='chemical/seq-aa-fasta')
        response['Content-Disposition'] = 'attachment; filename="'+gene_name+'.fas"'
    response['Content-Transfer'] = "Encoding: binary"
    response['Content-Length'] = myfile.tell()
    return response

def gene_test_ajax  (request, gene_name):
    if request.method == 'POST':
        gene_name = request.POST.get('gene_name')
        response_data = {}
        active_gene = get_object_or_404(gene, name=gene_name)
        response_data['matches'] = {}
        # print (active_gene.sequence)
        for single_clade in clade.objects.all():
            if single_clade.regExpr:
                reg_expr = "("+single_clade.regExpr+")"
                if single_clade.identifier in ['H26','H25']:
                    # print (single_clade.identifier,reg_expr)
                    pass
                reg = re.compile (reg_expr)
                iterator = reg.finditer(active_gene.sequence) 
                result = []
                for match in iterator:
                    print (match)
                    #print (single_clade.identifier)
                    #print (match)
                    region = ''
                    last = len(result)
                    result.append({})
                    #print (match.groups())
                    for idx in range(3, len(match.groups())+1):
                        # 12..34,24..45
                        region += '{}..{},'.format(match.start(idx)+1, match.end(idx))
                        # print (idx, match.group(idx))
                    region = region[:-1]
                    #print (region)
                    result[last]['region'] = region
                    result[last]['start'] =match.start(2)+1
                    result[last]['end'] =match.end(2)
                    response_data['matches'][single_clade.identifier] = result
                response_data["gene_name"] = gene_name
                #response_data['matches'][single_clade.identifier] = result
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        #print ("!")
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

def domains(request):
    domains = feature_type.objects.filter(domain_list = True)
    # print (domains)
    template = loader.get_template('database/domains.html')
    context = {
        'domains' : domains

    }
    return HttpResponse(template.render(context, request))

def domain_detail(request,domain_name):
    domain = feature_type.objects.get(name=domain_name)
    genes = domain.get_unique()
    # print (genes)
    template = loader.get_template('database/domain_detail.html')
    context = {
        'domain' : domain,
        'genes' : genes

    }
    return HttpResponse(template.render(context, request))

def download(request):
    # print (domains)
    template = loader.get_template('database/download.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def contact(request):
    # print (domains)
    template = loader.get_template('database/contact.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def info(request):
    # print (domains)
    template = loader.get_template('database/info.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

