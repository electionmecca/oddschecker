from __future__ import division
import scraperwiki
# This is a template for a Python scraper on Morph (https://morph.io)
# including some code snippets below that you should find helpful
    
constituencyslugs=['isle-of-wight']

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
        
def urlbuilder_constituency(constslug):
  return 'http://www.oddschecker.com/politics/british-politics/{0}/winning-party'.format(constslug)

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

def oddsGrabber2(soup,default):

  allbets=default
  allbets['time']=datetime.datetime.utcnow()
  bets={}
  allbets['odds']=bets
  
  if soup=="": return allbets
  
  table=soup.find( "tbody", {"id":"t1"} )
  if table is None: return allbets

  for row in table.findAll('tr'):
    name=row('td')[1].string
    tds = row('td')[3:]
    bets[name]={}
    for td in tds:
      if td.string!=None:
        try:
          bets[name][ td['id'].split('_')[1] ]=td.string
        except: pass
  allbets['odds']=bets
  return allbets

def oddsGrabber_constituency(constslug,default):
  url=urlbuilder_constituency(constslug)
  soup=makeSoup(url)
  if soup=='':
    return {}
  return oddsGrabber(soup,default)

def oddsParser(odds,bookies=[]):
  if 'odds' not in odds: return []
  bigodds=[]
  oddsdata=odds['odds']
  for party in oddsdata:
    #data in tidy format
    data={'time':odds['time'],'constituency':odds['const']}
    for bookie in oddsdata[party]:
      if bookies==[] or bookie in bookies:
      	data['party']=str(party)
      	data['bookie']=str(bookie)
      	data['oddsraw']=str(oddsdata[party][bookie])
      	try:
      		data['odds']=eval(data['oddsraw'])
      		bigodds.append(data.copy())
      	except: pass
      	 
  return bigodds

typ='IW2015GE'
dropper(typ)

scraperwiki.sqlite.execute("CREATE TABLE IF NOT EXISTS 'IW2015GE' ( 'time' datetime , 'bookie' text, 'party' text, 'odds' real, 'oddsraw' text, 'constituency' text)")

for const in constituencyslugs:
  odds=oddsGrabber_constituency(const,{'typ':typ,'const':const})
  oddsdata=oddsParser(odds)
  scraperwiki.sqlite.save(unique_keys=[],table_name=typ, data=oddsdata)




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
bigslugs=[('politics/british-politics/next-uk-general-election','next-government')]	
for path, slug in bigslugs:
  odds=oddsGrabber_generic(path,slug,{'typ':typ})
  oddsdata=oddsParser_generic(odds)
  scraperwiki.sqlite.save(unique_keys=[],table_name=typ, data=oddsdata)
 
 
 
 
#full...
from time import sleep

scraperwiki.sqlite.execute("CREATE TABLE IF NOT EXISTS 'constituency2015GE' ( 'time' datetime , 'bookie' text, 'party' text, 'odds' real, 'oddsraw' text, 'constituency' text)")

constituencyslugs=["aberavon","aberconwy","aberdeen-north","aberdeen-south","aberdeenshire-west-and-kincardine","airdrie-and-shotts","aldershot","aldridge-brownhills","altrincham-and-sale-west","alyn-and-deeside","amber-valley","angus","antrim-east","antrim-north","antrim-south","arfon","argyll-and-bute","arundel-and-south-downs","ashfield","ashford","ashton-under-lyne","aylesbury","ayr-carrick-and-cumnock","ayrshire-central","ayrshire-north-and-arran","banbury","banff-and-buchan","barking","barnsley-central","barnsley-east","barrow-and-furness","basildon-south-and-east-thurrock","basildon-and-billericay","basingstoke","bassetlaw","bath","batley-and-spen","battersea","beaconsfield","beckenham","bedford","bedfordshire-mid","bedfordshire-north-east","bedfordshire-south-west","belfast-east","belfast-north","belfast-south","belfast-west","bermondsey-and-southwark","berwick-upon-tweed","berwickshire-roxburgh-and-selkirk","bethnal-green-and-bow","beverley-and-holderness","bexhill-and-battle","bexleyheath-and-crayford","birkenhead","birmingham-edgbaston","birmingham-erdington","birmingham-hall-green","birmingham-hodge-hill","birmingham-ladywood","birmingham-northfield","birmingham-perry-barr","birmingham-selly-oak","birmingham-yardley","bishop-auckland","blackburn","blackley-and-broughton","blackpool-north-and-cleveley","blackpool-south","blaenau-gwent","blaydon","blyth-valley","bognor-regis-and-littlehampton","bolsover","bolton-north-east","bolton-south-east","bolton-west","bootle","boston-and-skegness","bosworth","bournemouth-east","bournemouth-west","bracknell","bradford-east","bradford-south","bradford-west","braintree","brecon-and-radnorshire","brent-central","brent-north","brentford-and-isleworth","brentwood-and-ongar","bridgend","bridgewater-and-west-somerset","brigg-and-goole","brighton-kemptown","brighton-pavilion","bristol-east","bristol-north-west","bristol-south","bristol-west","broadland","bromley-and-chislehurst","bromsgrove","broxbourne","broxtowe","buckingham","burnley","burton","bury-north","bury-south","bury-st-edmunds","caerphilly","caithness-sutherland-and-easter-ross","calder-valley","camberwell-and-peckham","camborne-and-redruth","cambridge","cambridgeshire-n-e","cambridgeshire-nw","cambridgeshire-south","cambridgeshire-south-east","cannock-chase","canterbury","cardiff-central","cardiff-north","cardiff-sth-and-penarth","cardiff-west","carlisle","carmarthen-est-and-dinefw","carmarthen-wst-and-sth-pembrokshire","carshalton-and-wallington","castle-point","ceredigion","charnwood","chatham-and-alyesford","cheadle","chelmsford","chelsea-and-fulham","cheltenham","chesham-and-amersham","chesterfield","chichester","chingford-and-woodford-gr","chippenham","chipping-barnet","chorley","christchurch","cities-of-london-and-west","city-of-durham","city-of-chester","clacton","cleethorpes","clwyd-south","clwyd-west","coatbridge-chryston-and-bellshill","colchester","colne-valley","congleton","copeland","corby","cornwall-north","cornwall-south-east","cotswolds","coventry-north-east","coventry-north-west","coventry-south","crawley","crewe-and-nantwich","croydon-central","croydon-north","croydon-south","cumbernauld-kilsyth-and-kirkintill","cynon-valley","dagenham-and-rainham","darlington","dartford","daventry","delyn","denton-and-reddish","derby-north","derby-south","derbyshire-dales","derbyshire-mid","derbyshire-north-east","derbyshire-south","devizes","devon-central","devon-east","devon-north","devon-sw","devon-west-and-torridge","dewsbury","don-valley","doncaster-central","doncaster-north","dorset-north","dorset-south","dorset-west","dover","down-north","down-south","dudley-north","dudley-south","dulwich-and-west-norwood","dumfries-and-galloway","dumfriesshire-clydesdale-and-tweeddale","dunbartonshire-east","dunbartonshire-west","dundee-east","dundee-west","dunfermline-and-west-fife","durham-north","durham-north-west","dwfor-meirionnydd","ealing-central-and-acton","ealing-north","ealing-southall","easington","east-ham","east-kilbride-strathaven-and-lesma","east-lothian","eastbourne","eastleigh","eddisbury","edinburgh-east","edinburgh-north-and-leith","edinburgh-south","edinburgh-south-west","edinburgh-west","edmonton","ellesmere-port-and-neston","elmet-and-rothwell","eltham","enfield-north","enfield-southgate","epping-forest","epsom-and-ewell","erewash","erith-and-thamesmead","esher-and-walton","exeter","falkirk","fareham","faversham-and-mid-kent","feltham-and-heston","fife-north-east","filton-and-bradley-stoke","finchley-and-golders-green","folkestone-and-hythe","forest-of-dean","foyle","fylde","gainsborough","garston-and-halewood","gateshead","gedling","gillingham-and-rainham","glasgow-central","glasgow-east","glasgow-north","glasgow-north-east","glasgow-north-west","glasgow-south","glasgow-south-west","glenrothes","gloucester","gordon","gosport","gower","grantham-and-stamford","gravesham","great-grimsby","great-yarmouth","greenwich-and-woolwich","guildford","hackney-north-and-stoke-newington","hackney-south-and-shoreditch","halesowen-and-rowley-regis","halifax","haltemprice-and-howden","halton","hammersmith","hampshire-east","hampshire-north-east","hampshire-north-west","hampstead-and-kilburn","harborough","harbough","harlow","harrogate-and-knaresborough","harrow-east","harrow-west","hartlepool","harwich-and-north-essex","hastings-and-rye","havant","hayes-and-harlington","hazel-grove","hemel-hempstead","hemsworth","hendon","henley","hereford-and-south-herefordshire","herefordshire-north","hertford-and-stortford","hertfordshire-ne","hertfordshire-south-wes","hertsmere","hexham","heywood-and-middleton","high-peak","hitchin-and-harpenden","holborn-and-st-pancras","hornchurch-and-upminster","hornsey-and-wood-green","horsham","houghton-and-sunderland-so","hove","huddersfield","hull-east","hull-north","hull-west-and-hessle","huntingdon","hyndburn","ilford-north","ilford-south","inverclyde","inverness-nairn-badenoch-and-strathspey","ipswich","isle-of-wight","islington-north","islington-s-and-finsbury","islwyn","jarrow","keighley","kenilworth-and-southam","kensington","kettering","kilmarnock-and-loudoun","kingston-upon-hull-north","kingston-and-surbiton","kingston-upon-hull-east","kingswood","kirkcaldy-and-cowdenbeath","knowsley","lagan-valley","lanark-and-hamilton-east","lancashire-west","lancaster-and-fleetwood","leeds-central","leeds-east","leeds-north-east","leeds-north-west","leeds-west","leicester-east","leicester-south","leicester-west","leicestershire-nw","leicestershire-south","leigh","lewes","lewisham-deptford","lewisham-east","lewisham-west-and-penge","leyton-and-wanstead","lichfield","lincoln","linlithgow-and-falkirk-ea","liverpool-riverside","liverpool-walton","liverpool-wavertree","liverpool-west-derby","livingston","llanelli","londonderry-east","loughborough","louth-and-horncastle","ludlow","luton-north","luton-south","macclesfield","maidenhead","maidstone-and-weald","makerfield","maldon","manchester-central","manchester-gorton","manchester-withington","mansfield","meon-valley","meriden","merthyr-tydfil-and-rhymney","mid-dorset-and-north-poole","middlesbrough","middlesbrough-south-and-east-cleveland","midlothian","milton-keynes-north","milton-keynes-south","mitcham-and-morden","mole-valley","monmouth","montgomeryshire","moray","morecambe-and-lunsdale","morley-and-outwood","motherwell-and-wishaw","na-h-eileanan-an-iar","neath","new-forest-east","new-forest-west","newark","newbury","newcastle-upon-tyne-cen","newcastle-upon-tyne-east","newcastle-upon-tyne-nrth","newcastle-under-lyme","newport-east","newport-west","newry-and-armagh","newton-abbot","norfolk-mid","norfolk-north","norfolk-north-west","norfolk-south","norfolk-south-west","normanton-pontefract-castleford","north-warwickshire","northampton-north","northampton-south","northamptonshire-south","norwich-north","norwich-south","nottingham-east","nottingham-north","nottingham-south","nuneaton","ochill-and-sth-perthshire","ogmore","old-bexley-and-sidcup","oldham-east-and-saddleworth","oldham-west-and-royton","orkney-and-shetland","orpington","oxford-east","oxford-west-and-abingdon","paisley-and-renf-north","paisley-and-renf-south","pendle","penistone-and-stocksbridge","penrith-and-the-border","perth-and-n-perthshire","peterborough","plymouth-moor-view","plymouth-sutton-and-devonport","pontypridd","poole","poplar-and-limehouse","portsmouth-north","portsmouth-south","preseli-pembrokeshire","preston","pudsey","putney","rayleigh-and-wickford","reading-east","reading-west","redcar","redditch","reigate","renfrewshire-east","rhondda","ribble-south","ribble-valley","richmond-park","richmond-yorks","rochdale","rochester-and-strood","rochford-and-southend-east","romford","romsey-and-southampton-north","ross-skye-and-lochaber","rossendale-and-darwen","rother-valley","rotherham","rugby","ruislip-northwood-and-pinner","runnymede-and-weybridge","rushcliffe","rutherglen-and-hamilton-west","rutland-and-melton","saffron-walden","salford-and-eccles","salisbury","scarborough-and-whitby","scunthorpe","sedgefield","sefton-central","selby-and-ainsty","sevenoaks","sheffield-brightside-and-hillsborough","sheffield-central","sheffield-hallam","sheffield-heely","sheffield-south-east","sherwood","shipley","shrewsbury-and-atcham","shropshire-north","sittingbourne-and-sheppey","skipton-and-ripon","sleaford-and-n-hykeham","slough","solihull","somerset-north","somerset-north-east","somerton-and-frome","south-holland-and-the-deepings","south-shields","southampton-itchen","southampton-test","southend-west","southport","spelthorne","st-albans","st-austell-and-newquay","st-helens-north","st-helens-south","st-ives","stafford","staffordshire-moorlands","staffordshire-south","stalybridge-and-hyde","stevenage","stirling","stockport","stockton-north","stockton-south","stoke-on-trent-central","stoke-on-trent-north","stoke-on-trent-south","stone","stourbridge","strangford","stratford-on-avon","streatham","stretford-and-urmston","stroud","suffolk-central-and-ipswich-north","suffolk-coastal","suffolk-south","suffolk-west","sunderland-central","surrey-east","surrey-heath","surrey-south-west","sussex-mid","sutton-coldfield","sutton-and-cheam","swansea-east","swansea-west","swindon-north","swindon-south","tamworth","tatton","taunton-deane","telford","tewkesbury","thanet-north","thanet-south","the-wrekin","thirsk-and-malton","thornbury-and-yate","thurrock","tiverton-and-honiton","tonbridge-and-malling","tooting","torbay","torfaen","totnes","tottenham","truro-and-falmouth","tunbridge-wells","twickenham","tynemouth","tyneside-north","tyrone-west","ulster-mid","upper-bann","uxbridge-and-south-ruislip","vale-of-clwyd","vale-of-glamorgan","vauxhall","wakefield","wallasey","walsall-north","walsall-south","walthamstow","wansbeck","wantage","warley","warrington-north","warrington-south","warwick-and-leamington","washington-and-sunderland-west","watford","waveney","wealden","weaver-vale","wellingborough","wells","welwyn-hatfield","wentworth-and-dearne","west-bromwich-east","west-bromwich-west","west-ham","westminster-north","westmorland-and-lonsdale","weston-super-mare","wigan","wiltshire-north","wiltshire-south-west","wimbledon","winchester","windsor","wirral-south","wirral-west","witham","witney","woking","wokingham","wolverhampton-n-east","wolverhampton-s-east","wolverhampton-s-west","worcester","worcestershire-mid","worcestershire-west","workington","worsley-and-eccles-south","worthing-east-and-shoreham","worthing-west","wrexham","wycombe","wyre-forest","wyre-and-preston-north","wythenshawe-and-sale-east","yeovil","ynys-mon","york-central","york-outer","yorkshire-east"]

for const in constituencyslugs:
  sleep(0.1)
  print(const)
  odds=oddsGrabber_constituency(const,{'typ':typ,'const':const})
  oddsdata=oddsParser(odds,['LD','B3','WH','FB'])
  scraperwiki.sqlite.save(unique_keys=[],table_name='constituency2015GE', data=oddsdata)






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
