from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from django.utils.http import urlquote_plus

import os
import urllib2
import urllib
import json
#import logging
import datetime

from suds.client import Client
from suds.sax.element import Element
from suds.bindings import binding
from suds import WebFault
from suds.transport.http import HttpTransport as SudsHttpTransport

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

from suds.client import Client

logger = logging.getLogger(__name__)
binding.envns=('SOAP-ENV','http://www.w3.org/2003/05/soap-envelope')

PROXY_FORMAT = u"https://%s/%s" % (settings.PROXY_DOMAIN, u"%s")
    
def covr_proxy(values):
#    if 'http_proxy' in os.environ:
#        print os.environ['http_proxy']
#    else:
#        tmp_http_proxy = None
    if 'https_proxy' in os.environ:
        print os.environ['https_proxy']
#    else:
#        tmp_https_proxy = None
        
    #os.environ['http_proxy'] = os.environ['PROXIMO_URL']
    #os.environ['https_proxy'] = os.environ['PROXIMO_URL'] + ':80'
    #os.environ['http_proxy'] = os.environ['QUOTAGUARDSTATIC_URL']
    #os.environ['https_proxy'] = os.environ['QUOTAGUARDSTATIC_URL']

    #url = 'https://d353l29op77hfl.cloudfront.net/static/CA-PostingEntityPreSave-wsdl.xml'
    #production wsdl
    url = 'https://d31f4s4vpq6rg9.cloudfront.net/static/CA-PostingEntityPreSave-wsdl.xml'
    #if settings.DEBUG: 
    #print 'Debug Mode: ' + settings.DEBUG
    print values

    print 'Creating suds Client'

    covr_client = Client(url)
  
    print 'Setting Proxy'
    d = dict(http='PROXIMO-URL',
             https='PROXIMO-URL')
    print d
    covr_client.set_options(proxy=d)
    print 'Proxy set'
    covr_client.set_options(headers={'Content-Type':'application/soap+xml; charset=utf-8'})
    wsans = ('wsa', 'http://www.w3.org/2005/08/addressing')
    msgId1 = Element('Action', ns=wsans).setText('http://tempuri.org/IPostingEntityInterfaceService/GetTokenNumber')
    msgId2 = Element('To', ns=wsans).setText('https://covrapi.sos.ca.gov/PostingEntityInterfaceService.svc')
    covr_client.set_options(soapheaders=[msgId1,msgId2])

    dob = datetime.datetime.strptime(values['date_of_birth'],"%m/%d/%Y").date()
    prefixId = 0
    if values['name_title'] == 'Mr.':
        prefixId = 1
    elif values['name_title'] == 'Mrs.':
        prefixId = 2
    elif values['name_title'] == 'Miss':
        prefixId = 3
    elif values['name_title'] == 'Ms.':
        prefixId = 4
        
    if values['home_address'] == '':
        HomeAddressStreetLine1 = 0
    
    print covr_client
    print 'Creating postingEntity'
    postingEntity = covr_client.factory.create('PostingEntity')
    postingEntity.PostingAgencyKey = 'NEEDKEY'
    postingEntity.VoterResidentType = 1
    postingEntity.IsDisclosureDisplayed = 1
    #postingEntity.IsUsCitizen = 1
    postingEntity.IsUsCitizen = values['us_citizen']
    postingEntity.IsEighteenOrOlder = 1
    #postingEntity.CovrAgencyKey='RTV'
    postingEntity.DobDay=dob.day
    postingEntity.DobMonth=dob.month
    postingEntity.DobYear=dob.year
    postingEntity.ElectionMaterialLanguageId=2
    postingEntity.PrefixId=prefixId
    #postingEntity.CurrentFirstName='first_name'
    postingEntity.CurrentFirstName=values['first_name']
    #postingEntity.CurrentMiddleName=''
    #postingEntity.CurrentLastName='last_name'
    postingEntity.CurrentLastName=values['last_name']
    #postingEntity.PreviousFirstName=
    #postingEntity.PreviousMiddleName=
    #postingEntity.PreviousLastName=
    postingEntity.IsHomeAddress=1
    postingEntity.HomeAddressStreetLine1=values['home_address']
    #postingEntity.HomeAddressStreetLine2='234'
    postingEntity.HomeAddressCity=values['home_city']
    postingEntity.HomeAddressState='California'
    postingEntity.HomeAddressZip=values['home_zip_code']
    postingEntity.IsMailingAddress=0
    #postingEntity.MailingAddressStreetLine1='1939 mail ste1'
    #postingEntity.MailingAddressStreetLine2='asdf'
    #postingEntity.MailingAddressCity='Bev Hills'
    #postingEntity.MailingAddressState='California'
    #postingEntity.MailingAddressZip='90210'
    postingEntity.IsPreviouslyRegistered=0
    #postingEntity.PreviousAddressStreetLine1=
    #postingEntity.PreviousAddressStreetLine2=
    #postingEntity.PreviousAddressCity=
    #postingEntity.PreviousAddressState=
    #postingEntity.PreviousAddressZip=
    postingEntity.PhoneNumber=values['phone']
    postingEntity.EmailId=values['email_address']
    #postingEntity.EmailIdConfirmation=
    postingEntity.IsNonUspsAddress = 0
    postingEntity.EthnicityId = 0
    postingEntity.DobStateId=0
    postingEntity.DobCountryId=0

    try:
        print postingEntity
        print 'Calling GetTokenNumber Service'
        result=covr_client.service.GetTokenNumber(postingEntity)
        print 'Returned from GetTokenNumber Service'
    except WebFault, f:
        print f
        print f.fault
    except Exception, e:
        print e

    print result

    return result

def rtv_proxy_view(request,url):
    #wrapper for direct django view
    if request.method == "GET":
        response = rtv_proxy("GET",request.GET,url)
    elif request.method == "POST":
        response = rtv_proxy("POST",request.GET,url)
    elif request.method == "HEAD":
        exists = url_exists(PROXY_FORMAT % url)
        response = {'exists':exists,
            'error':not exists,
        }
        if exists:
            response['status'] = 200
        else:
            response['status'] = 404
    try:
        if response.has_key('error'):
            status = response['status']
        else:
            status = 200
    except UnboundLocalError:
        response = {'error':'unknown rtv proxy error'}
        status = 404
    return HttpResponse(json.dumps(response),mimetype="application/json",status=status)

def rtv_proxy(method, values, url):
    if settings.DEBUG: print "PROXY",method,
    if method == "GET":
        if settings.DEBUG: print values
        data = urllib.urlencode(values)
        url_ending = "%s?%s" % (url, data)
        url = PROXY_FORMAT % url_ending
    elif method == "POST":
        if settings.DEBUG: print values
        url = PROXY_FORMAT % url
        if 'registrations.json' in url:
            #don't use urllib.urlencode to encode data dictionary,
            #that munges the brackets, quote_plus the values and do &-join manually
            data = []
            for (k,v) in values.items():
                v_s = unicode(v).strip() #strip spaces, because rocky doesn't like them
                data.append('registration[%s]=%s' % (k,urlquote_plus(v_s)))
            data = "&".join(data)
        else:
            data = urllib.urlencode(values)
        if settings.DEBUG: print "POST QUERY",data
    
    if hasattr(settings,'PROXY_CREDENTIALS'):
        #setup a password manager to handle the authentication
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        url_opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(url_opener)
        #password_manager.add_password(None, url, #none means don't specify realm
                                      #settings.PROXY_CREDENTIALS['rtvdemo'],
                                      #settings.PROXY_CREDENTIALS['bullwinkle'])
        password_manager.add_password(None, url, "rtvdemo", "bullwinkle")
    try:
        if method == "GET":
            response = urllib2.urlopen(url)
        elif method == "POST":
            response = urllib2.urlopen(url,data)
    except urllib2.HTTPError,e:
        error_message = e.read()
        logger.error('rocky api error: %s' % e.code,exc_info=True,extra={'error_message':error_message})
        try:
            error_dict = {'error':json.loads(error_message)}
        except ValueError:
            error_dict = {'error':error_message}
        error_dict['status'] = e.code
        return error_dict
        
    content = response.read()
    return json.loads(content)

def rtv_proxy_cached(method, values, url):
    #cached proxy, should probably only be used for getting state requirements
    cache_key = "%s:%s:%s" % (method,url, ".".join(values.values()))
    if cache.get(cache_key):
        if settings.DEBUG: print "cache.get", cache_key
        return cache.get(cache_key)
    else:
        response = rtv_proxy(method,values,url)
        cache.set(cache_key,response,1)
        if settings.DEBUG: print "cache.set", cache_key
        return response


def url_exists(url):
    #use HEAD method to get only response code, not full contents
    class HeadRequest(urllib2.Request):
        def get_method(self):
            return "HEAD"

    try:
        response = urllib2.urlopen(HeadRequest(url))
        return (response.code == 200)
    except urllib2.HTTPError:
        return False
    except Exception,e:
        if settings.DEBUG: print e
        return False

def partner_proxy(method,url,values):
    #values should be a dictionary at this point
    if settings.DEBUG: print "PARTNER PROXY",method

    if method == "POST":
        data = urllib.urlencode(values)
        try:
            response = urllib2.urlopen(url,data)
        except urllib2.HTTPError,e:
            error_dict = {'error':json.loads(e.read())}
            error_dict['status'] = e.code
            return error_dict

        if settings.DEBUG: print "PARTNER PROXY DATA",data

        content = response.read()
        return json.loads(content)
