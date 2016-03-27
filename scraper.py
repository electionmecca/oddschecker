from __future__ import division
import scraperwiki
# This is a template for a Python scraper on Morph (https://morph.io)
# including some code snippets below that you should find helpful
    

#nodrop - 0 if you want to drop, 1 if you don't
nodrop=1

import requests
import datetime
from bs4 import BeautifulSoup
from lxml import html

def dropper(table):
    """ Helper function to drop a table """
    if nodrop==1: return
    print "dropping",table
    if table!='':
        try: scraperwiki.sqlite.execute('drop table "'+table+'"')
        except: pass
        
def oddsGrabber(tree,default):
    allbets=default
    allbets['time']=datetime.datetime.utcnow()
    bets={}
    allbets['odds']=bets
  
    if tree=="" or tree is None: return allbets

    for row in tree.xpath('//tbody[@id="t1"]/tr'):
        name=row[1].text
        bets[name]={}
        for cell in row[3:]:
            if cell.text is not None:
                try:
                    bets[name][ cell.get('id').split('_')[1] ]=cell.text
                except: pass
    allbets['odds']=bets
    #print(allbets)
    return allbets
    
def makeSoup(url):
	try:
		r = requests.get(url)
		#print '>>>',r.history
		#ret= BeautifulSoup(r.text)
		ret=html.fromstring(r.text)
		for s in r.history:
			if s.status_code==302: ret==""
	except: ret=""
	return ret

#General election overall

def urlbuilder_generic(path,slug):
  return 'http://www.oddschecker.com/{0}/{1}'.format(path,slug)

def oddsGrabber_generic(path,slug,default):
  url=urlbuilder_generic(path, slug)
  soup=makeSoup(url)
  if soup=='':
    return {}
  return oddsGrabber(soup,default)

def oddsParser_generic(odds,bookies=[]):
  bigodds=[]
  oddsdata=odds['odds']
  for outcome in oddsdata:
    #data in tidy format
    data={'time':odds['time'],'typ':odds['typ']}
    for bookie in oddsdata[outcome]:
      if bookies==[] or bookie in bookies:
      	data['outcome']=str(outcome)
      	data['bookie']=str(bookie)
      	data['oddsraw']=str(oddsdata[outcome][bookie])
      	try:
      		data['odds']=eval(str(data['oddsraw']))
      		bigodds.append(data.copy()) 
      	except: pass
      	
  return bigodds

typ='overall2015GE'
dropper(typ)

scraperwiki.sqlite.execute("CREATE TABLE IF NOT EXISTS 'overall2015GE' ( 'time' datetime , 'bookie' text, 'outcome' text, 'odds' real, 'oddsraw' text, 'typ' text)")
bigslugs=[('politics/us-politics/us-presidential-election-2016','winning-party')]	
for path, slug in bigslugs:
  odds=oddsGrabber_generic(path,slug,{'typ':typ})
  oddsdata=oddsParser_generic(odds)
  scraperwiki.sqlite.save(unique_keys=[],table_name=typ, data=oddsdata)
 
 
 
 
#full...
#from time import sleep






# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries. You can use whatever libraries are installed
# on Morph for Python (https://github.com/openaustralia/morph-docker-python/blob/master/pip_requirements.txt) and all that matters
# is that your final data is written to an Sqlite database called data.sqlite in the current working directory which
# has at least a table called data.
