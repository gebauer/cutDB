# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^genes/$', views.genes, name='genes'),
    url(r'^genes/add_clades/$', views.gene_add_clade, name='add_clade_to_gene'),
    url(r'^genes/(?P<gene_name>[^/]+)/$', views.gene_detail, name='gene_info'),
    url(r'^genes/(?P<gene_name>[^/]+)/test$', views.gene_test_ajax, name='test_gene'),
    url(r'^genes/(?P<gene_name>[^/]+)/export/(?P<format>.+)/$', views.gene_export_ajax, name='export_gene'),
    url(r'^genes/(?P<gene_name>[^/]+)/add/(?P<clade_identifier>.+)/$', views.gene_add_clade, name='add_clade_to_gene'),
    url(r'^clades/$', views.clades, name='clades'),
    url(r'^clades/(?P<clade_identifier>[^/]+)/$', views.clade_detail, name='clade_info'),
    url(r'^clades/(?P<clade_identifier>[^/]+)/export/(?P<format>.+)/(?P<rec>.+)/$', views.clade_export_ajax, name='export_clade'),
    url(r'^domains/$', views.domains, name='domains'),
    url(r'^domains/(?P<domain_name>[^/]+)/$', views.domain_detail, name='domain_info'),
    url(r'^download/$', views.download, name='download'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^info/$', views.info, name='info'),


]