#!/usr/bin/env python
# coding: utf-8

import os
import re
import numpy as np
import pandas as pd
import metapub
from metapub import PubMedFetcher
from metapub import CrossRefFetcher
from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json

data = pd.read_excel('CodeInput.xlsx').fillna(0)
title = np.array(data['Title'])
pmids = np.array(data['Medline_PMID'])
np.nan_to_num(title)
cr = CrossRefFetcher()
PM = PubMedFetcher()

#From Elsevier's Developer Tools
#Create the config.json and make sure it is
#in the same folder directory as the script

con_file = open("config.json")
config = json.load(con_file)
con_file.close()
client = ElsClient(config['apikey'])

count = 0
for pmid in pmids:
    print(count)
    if pmid != 0.0:
        try:
            article = PM.article_by_pmid(pmid)
            tag = "PM"
            print('Yes PM')
        except:
            try:
                article = cr.article_by_title(title[count])
                tag = "CR"
                print('Yes CR')
            except:
                count = count + 1
                data.Notes[count] = "Failed"
                tag = "Failed"
                print('Could not find 1')
    else:
        try:
            article = cr.article_by_title(title[count])
            print('Yes CR trying PM')
            try:
                article = PM.article_by_doi(article.doi)
                tag = "PM"
                print('PM Works')
            except:
                doi_doc = FullDoc(doi=article.doi)
                doi_doc.read(client)
                if doi_doc.data is None:
                    data.Notes[count] = "Failed"
                    print('Could not find 2')
                    tag = "Failed"
                else:
                    tag = "EL"
                    print("Last resort")
        except:
            count = count + 1
            data.Notes[count] = "Failed"
            print("Could not find 3")   
    data.URL[count] = article.doi
    data.Notes[count] = article.title
    data.Tag[count] = tag
    if tag == "PM":
        if 'Review' in article.publication_types.values():
            data.Publication_Type[count] = 'Review'
        elif 'Editorial' in article.publication_types.values():
            data.Publication_Type[count] = 'Editorial'
        elif 'Case Reports' in article.publication_types.values():
            data.Publication_Type[count] = 'Case Report'
        elif 'Journal Article' in article.publication_types.values():
            data.Publication_Type[count] = 'Journal Article'
        else:
            data.Publication_Type[count] = str(article.publication_types.values())
        if article.title is None:
            data.Autism_title[count] = -99.0
            data.ASD_title[count] = -99.0
            data.Autism_Spectrum_Disorder_title[count] = -99.0
            data.ABIDE_title[count] = -99.0
            data.Autism_Brain_Imaging_Data_Exchange_title[count] = -99.0
        else:
            data.Autism_title[count] = article.title.lower().find('autism')
            data.ASD_title[count] = article.title.find('ASD')
            data.Autism_Spectrum_Disorder_title[count] = article.title.lower().find('autism spectrum disorder')
            data.ABIDE_title[count] = article.title.find('ABIDE')
            data.Autism_Brain_Imaging_Data_Exchange_title[count] = article.title.lower().find('autism brain imaging data exchange')
        if article.abstract is None:
            data.Autism_abstract[count] = -99.0
            data.ASD_abstract[count] = -99.0
            data.Autism_Spectrum_Disorder_abstract[count] = -99.0
            data.ABIDE_abstract[count] = -99.0
            data.Autism_Brain_Imaging_Data_Exchange_abstract[count] = -99.0
        else:
            data.Autism_abstract[count] = article.abstract.lower().find('autism')
            data.ASD_abstract[count] = article.abstract.find('ASD')
            data.Autism_Spectrum_Disorder_abstract[count] = article.abstract.lower().find('autism spectrum disorder')
            data.ABIDE_abstract[count] = article.abstract.find('ABIDE')
            data.Autism_Brain_Imaging_Data_Exchange_abstract[count] = article.abstract.lower().find('autism brain imaging data exchange')
        data.Medline_PMID[count] = article.pmid
    if tag == "CR":
        if str(article.reference).find('Di Martino') != -1:
            data.Citation[count] = "Yes"
        if article.title is None:
            data.Autism_title[count] = -99.0
            data.ASD_title[count] = -99.0
            data.Autism_Spectrum_Disorder_title[count] = -99.0
            data.ABIDE_title[count] = -99.0
            data.Autism_Brain_Imaging_Data_Exchange_title[count] = -99.0
        else:
            data.Autism_title[count] = str(article.title).lower().find('autism')
            data.ASD_title[count] = str(article.title).find('ASD')
            data.Autism_Spectrum_Disorder_title[count] = str(article.title).lower().find('autism spectrum disorder')
            data.ABIDE_title[count] = str(article.title).find('ABIDE')
            data.Autism_Brain_Imaging_Data_Exchange_title[count] = str(article.title).lower().find('autism brain imaging data exchange')
    elif tag == "EL":
        if doi_doc.data is None:
            count = count + 1
        else:
            data.Publication_Type[count] = doi_doc.data['coredata']['prism:aggregationType']
            data.Notes[count] = doi_doc.data['coredata']['dc:title']

            if doi_doc.data['coredata']['dc:title'] is None:
                data.Autism_title[count] = -99.0
                data.ASD_title[count] = -99.0
                data.Autism_Spectrum_Disorder_title[count] = -99.0
                data.ABIDE_title[count] = -99.0
                data.Autism_Brain_Imaging_Data_Exchange_title[count] = -99.0
            else:
                data.Autism_title[count] = doi_doc.data['coredata']['dc:title'].lower().find('autism')
                data.ASD_title[count] = doi_doc.data['coredata']['dc:title'].find('ASD')
                data.Autism_Spectrum_Disorder_title[count] = doi_doc.data['coredata']['dc:title'].lower().find('autism spectrum disorder')
                data.ABIDE_title[count] = doi_doc.data['coredata']['dc:title'].find('ABIDE')
                data.Autism_Brain_Imaging_Data_Exchange_title[count] = doi_doc.data['coredata']['dc:title'].lower().find('autism brain imaging data exchange')

            if doi_doc.data['coredata']['dc:description'] is None:
                data.Autism_abstract[count] = -99.0
                data.ASD_abstract[count] = -99.0
                data.Autism_Spectrum_Disorder_abstract[count] = -99.0
                data.ABIDE_abstract[count] = -99.0
                data.Autism_Brain_Imaging_Data_Exchange_abstract[count] = -99.0
            else:
                data.Autism_abstract[count] = doi_doc.data['coredata']['dc:description'].lower().find('autism')
                data.ASD_abstract[count] = doi_doc.data['coredata']['dc:description'].find('ASD')
                data.Autism_Spectrum_Disorder_abstract[count] = doi_doc.data['coredata']['dc:description'].lower().find('autism spectrum disorder')
                data.ABIDE_abstract[count] = doi_doc.data['coredata']['dc:description'].find('ABIDE')
                data.Autism_Brain_Imaging_Data_Exchange_abstract[count] = doi_doc.data['coredata']['dc:description'].lower().find('autism brain imaging data exchange')
    count = count + 1
    data.to_csv('DataMind_Results.csv')  



