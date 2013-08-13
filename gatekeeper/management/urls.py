# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url


urlpatterns = patterns('gatekeeper.management.views',
    
    url(r'^$',"org_manage",name="gk_org_manage"),
    
    url(r'^org-tree/$',"org_tree",name="gk_org_tree"),
    url(r'^org-node/$',"org_node",name="gk_org_node"),
    
    url(r'^get-node-member/$',"get_node_member",name="gk_get_node_member"),
    url(r'^get-node-signer-member/$',"get_node_signer_member",name="gk_get_node_signer_member"),
    
    url(r'^add-signer/$',"add_signer",name="gk_add_signer"),
    url(r'^remove-signer/$',"remove_signer",name="gk_remove_signer"),
    url(r'^move-member$',"move_member",name="gk_move_member"),
    
    url(r'^search-member$',"search_member",name="gk_member_search"),
    url(r'^add-member$',"add_member",name="gk_add_member"),
)
