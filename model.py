import re
import json
import requests
import sys
from dateutil.parser import parse
from datetime import timedelta
from time import sleep
from numpy.random import rand
import pickle
from collections import Counter
import pandas as pd

def rep (text, kv):
    for k, v in kv.items():
        subb=re.compile(k,re.IGNORECASE)
        text=subb.sub(v,text)
    return text

def easy_ner(series):
    mtc=list()
    for i in series:
        possible_matches=re.findall('((?:[\w]{,13}[\.]{,1}[\s]{,1}){,12})\(([\w\-]{2,6})\)', i)
        mtc.extend(possible_matches)
    return mtc

def get_pchange( endpoint, p, newvals):
    """
    Description:
        restful get from endpoint "endpoint" with parameters "p"
        replace a single parameter named "name" with "value"
    Assumptions:
        Fed Reg API - internal values assume this is so.
    """
    data=list()
    session=requests.Session()
    page=1
    p.update(newvals)
    while True:
        response = session.get(endpoint,params=p)
        c=response.content
        try:
            djson = json.loads(c)
        except:
            break
        count=str(djson['count'])+'/'+str(djson['total_pages']) if djson.get('total_pages') is not None else '???'
        sys.stdout.write(' Page {}, count & pages {}     \r'.format(page,count))
        sys.stdout.flush()
        page+=1
        results=djson.get('results')
        if(results is not None):
            data.extend(results)

        endpoint=djson.get('next_page_url')
        p=dict()
        if(endpoint is None):
            break
    return data

def __format_fedreg__(reg, mca):
    """
    Description:
        when used with apply, this takes a single reg record and extracts some nice information from it.

    """
    r=dict()
    r.update({'action_is_final': False if reg['action'] is None  else  re.search('final', reg['action'].lower()) is not None })
    r.update({'action_is_temp':  False if reg['action'] is None  else  re.search('temporary', reg['action'].lower()) is not None })
    r.update({'action_is_interim':  False if reg['action'] is None  else  re.search('interim', reg['action'].lower()) is not None })
    r.update({'requests_comments':  False if reg['action'] is None  else  re.search('comments', reg['action'].lower()) is not None })

    r.update({'abstract': rep(reg['abstract'], mca) if reg['abstract'] is not None else ''})
    r.update({'type':reg['type']})
    r.update({'title': rep(reg['title'], mca) if reg['title'] is not None else ''})
    r.update({'topics':[i.lower() for i in reg['topics']]})
    r.update({'president':reg['president']['identifier']})
    r.update({'publication_date':parse(reg['publication_date'])})
    r.update({'significant':reg['significant']})
    r.update({'agency_names':[ i for i in reg['agency_names'] if i.lower() in mca.keys()]})
    r.update({'cfr_ref_title':[i['title'] for i in reg['cfr_references']]})
    return r

class fedreg(object):
    def __init__(self, first_date='2001-01-20',last_date='2017-01-19', pp='2000', file=None):

        if file:
            try:
                with open(file,'rb') as datfile:
                    self.data=pickle.load(datfile)
            except:
                print("Unable to load data from pickle")
            else:
                print("successfully loaded data from pickle. Ignore all else")
        else:
            #stay the same
            self.__api_endpoint__='https://www.federalregister.gov/api/v1/documents.json'
            self.__fields__=['action','agency_names','abstract','title',
                    'cfr_references','corrections','dates','publication_date',
                    'effective_on','excerpts',
                    'president','significant','signing_date','type',
                    'executive_order_notes','topics']

            self.data=None
            #can change
            self.per_page=pp
            self.first_date=first_date
            self.last_date=last_date
            self.set_params()

    def __repr__(self):
        '''
        Description:
            reports back what is being run
        '''
        a=self.__api_endpoint__, self.first_date, self.last_date, ',\n\t\t'.join(self.__fields__), self.per_page
        g = '---\nAPI Endpoint:\t{} '
        g += '\nFirst Date:\t{}\nLast Date:\t{}'
        g += '\nFields:\t\t{}'
        g += '\nPer Page:\t{}'
        r = g.format(*a)
        return r




    def set_params(self):
        '''
        Description:
            sets parameters - wrote this so that i could change params easily after setting values later (when tweaking)
        '''
        conditions_type='RULE'
        AA = 'conditions[publication_date][gte]'
        BB = 'conditions[publication_date][lte]'
        self.params={'fields[]':self.__fields__,'conditions[type][]':conditions_type,
        'per_page':self.per_page,
        AA:self.first_date,
        BB:self.last_date}
        self.daterange=[]
        aa=self.first_date
        i = int(self.first_date[:4])+1
        while i<int(self.last_date[:4]):
            g = parse(str(i)+aa[4:])
            bb = (g-timedelta(days=1)).strftime('%Y-%m-%d')
            self.daterange.append({AA:aa,BB:bb})
            aa = g.strftime('%Y-%m-%d')
            i += 1
        bb=self.last_date
        self.daterange.append({AA:aa,BB:bb})


    def getData(self, sample=False):
        '''
        Description:
            Get data from Federal Register - N.B. had problems with only getting back 10x 1000 (10000) results, not the 60 K expected.
            So I split it up by year.
        '''


        #return 'data' if already exists. a bit fragile
        if self.data :
            return self.data

        g=requests.get(self.__api_endpoint__, self.params)
        samp=json.loads(g.content)

        # Was not always receiving number of records avaialble, so I print out the value to make sure
        try:
            total_counts=samp['count']
            print('Total Count is {}'.format(total_counts))
        except:
            pass

        # if "sample", then return whatever was provided so far- just checking!
        if sample:
            return samp

        #tried to use some better tools here, but in limited time did not work.
        self.data=list()
        for i in self.daterange:
            self.data.extend(get_pchange(self.__api_endpoint__, self.params,i))
            sys.stdout.write('\n')
            sys.stdout.flush()
        return self.data

    def formatedData(self):
        agencies=[ a for i in self.data for a in i['agency_names']]
        mca= set(list(map(lambda x: x[0] if x[1]>3  else 'Other',  Counter(agencies).most_common())))
        mca= {i.lower():'_agency_{:03d}'.format(j) for j, i in enumerate(mca)}
        self.agency_dictionary=mca
        data=list(map(lambda x: __format_fedreg__(x, mca), self.data))


        dfdata=pd.DataFrame(data)
        return dfdata
