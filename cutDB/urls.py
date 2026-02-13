# -*- coding: utf-8 -*-

from django.urls import include, re_path
from django.contrib import admin

from database import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^genes/$', views.genes, name='genes'),
    re_path(r'^genes/(?P<gene_name>[^/]+)/$', views.gene_detail, name='gene_info'),
    re_path(r'^genes/add_clades/$', views.gene_add_clade, name='add_clade_to_gene'),
    re_path(r'^genes/(?P<gene_name>[^/]+)/test$', views.gene_test_ajax, name='test_gene'),
    re_path(r'^genes/(?P<gene_name>[^/]+)/export/(?P<format>.+)/$', views.gene_export_ajax, name='export_gene'),
    re_path(r'^genes/(?P<gene_name>[^/]+)/add/(?P<clade_identifier>.+)/$', views.gene_add_clade, name='add_clade_to_gene'),
    re_path(r'^clades/$', views.clades, name='clades'),
    re_path(r'^clades/(?P<clade_identifier>[^/]+)/$', views.clade_detail, name='clade_info'),
    re_path(r'^clades/(?P<clade_identifier>[^/]+)/export/(?P<format>.+)/(?P<rec>.+)/$', views.clade_export_ajax, name='export_clade'),
    re_path(r'^domains/$', views.domains, name='domains'),
    re_path(r'^domains/(?P<domain_name>[^/]+)/$', views.domain_detail, name='domain_info'),
    re_path(r'^download/$', views.download, name='download'),
    re_path(r'^contact/$', views.contact, name='contact'),
    re_path(r'^info/$', views.info, name='info'),
]