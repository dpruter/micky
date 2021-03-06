from proxy.models import CustomForm,CoBrandForm
from proxy.views import rtv_proxy
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def cleanup_form(form):
    """Util method to cleanup user submitted form, in preparation for sending to Rocky"""

    #remove inputs that we needed, but the api will reject
    remove_inputs = ['csrfmiddlewaretoken','facebook','registrant_has_state_license_1','IsDisclosureDisplayed']
    for t in remove_inputs:
        if form.has_key(t):
            form.pop(t)

    #and add the ones it does
    form['send_confirmation_reminder_emails'] = '1'
    form['IsEighteenOrOlder'] = '1'

    #rename source to source_tracking_id as per api
    if 'source' in form:
        form['source_tracking_id'] = form.pop('source')[0]

    #convert "on/off" to "boolean" values expected by api
    booleans = ['us_citizen','first_registration','has_mailing_address','IsEighteenOrOlder',
                'change_of_name','change_of_address','us_citizen',
                'opt_in_sms','opt_in_email','opt_in_volunteer',
                'partner_opt_in_sms','partner_opt_in_email','partner_opt_in_volunteer']
    for b in booleans:
        if form.has_key(b):
            try:
                form[b] = int(form[b])
            except ValueError:
                #print "value error converting int(form[%s])" % b
                if form.get(b) == "off":
                    #print "setting form[%s] = off" % b
                    form[b] = 0
                if form.get(b) == "on":
                    #print "setting form[%s] = on" % b
                    form[b] = 1

    #check for rocky required fields, fill them with defaults
    #required_fields = ['us_citizen']
    required_fields = ['opt_in_sms','opt_in_email','us_citizen']
    for r in required_fields:
        if not r in form:
            #and fill it in with zero
            form[r] = 0
            print "setting form[%s] = 0" % r

    #check for title and replace it if it's an invalid value
    if 'name_title' in form:
        title = form.get('name_title')
        if title not in ["Mr.", "Ms.", "Mrs.", "Sr.", "Sra.","Srta.","Miss"]:
            form['name_title'] = "Mr." #guess, because we have to send valid data to API

    #check for suffix and clear it if it's an invalid value
    if 'name_suffix' in form:
        suffix = form.get('name_suffix')
        if suffix not in ["Jr.", "Sr.", "II", "III", "IV"]:
            form['name_suffix'] = ""

    #check for race and clear it if it's an invalid value
    if 'race' in form:
        race = form.get('race')
        if race not in ["American Indian / Alaskan Native", "Asian / Pacific Islander",
                        "Black (not Hispanic)", "Hispanic", "Multi-racial",
                        "White (not Hispanic)", "Other", "Decline to State",
                        "Indio Americano / Nativo de Alaska", "Asiatico / Islas del Pacifico",
                        "Negra (no Hispano)", "Hispano", "Blanca (no Hispano)", "Otra", "Declino comentar"]:
            form['race'] = "Other"

    
    #strip leading and trailing space from open text fields
    strip_fields = ['id_number','email_address','race','first_name','last_name','home_address']
    for f in strip_fields:
        if f in form:
            form[f] = form[f].strip()
            
    #replace any other spaces in id_number, because rocky doesn't like them
    if 'id_number' in form:
        if (' ' in form['id_number']):
            form['id_number'] = form['id_number'].replace(' ','')
            
        #if id_number blank, fill it in with none
        if empty(form['id_number']):
            form['id_number'] = "none"
            
    #replace any plus signs in first name, because rocky doesn't like them
    if 'first_name' in form:
        if ('+' in form['first_name']):
            form['first_name'] = form['first_name'].replace('+','')
            
    #replace any ' signs in first name, because rocky doesn't like them
    if 'first_name' in form:
        if ('\'' in form['first_name']):
            form['first_name'] = form['first_name'].replace('\'','')
            
    #replace any plus signs in last name, because rocky doesn't like them
    if 'last_name' in form:
        if ('+' in form['last_name']):
            form['last_name'] = form['last_name'].replace('+','')
    
    #replace any ' signs in last name, because rocky doesn't like them
    if 'last_name' in form:
        if ('\'' in form['last_name']):
            form['last_name'] = form['last_name'].replace('\'','')
            
    #covert & symbol in address, because rocky doesn't like them and people use
    if 'home_address' in form:
        if ('&' in form['home_address']):
            form['home_address'] = form['home_address'].replace('&','and')
            
    #covert : symbol in address, because rocky doesn't like them and people use
    if 'home_address' in form:
        if (':' in form['home_address']):
            form['home_address'] = form['home_address'].replace(':',' ')
    
    #covert ' symbol in address, because rocky doesn't like them and people use
    if 'home_address' in form:
        if ('\'' in form['home_address']):
            form['home_address'] = form['home_address'].replace('\'','')
    
    #covert , symbol in address, because rocky doesn't like them and people use
    if 'home_address' in form:
        if (',' in form['home_address']):
            form['home_address'] = form['home_address'].replace(',','')
    
    #covert + symbol in address, because rocky doesn't like them and people use
    if 'home_address' in form:
        if ('+' in form['home_address']):
            form['home_address'] = form['home_address'].replace('+',' ')
            
    #covert & symbol in address, because rocky doesn't like them and people use
    if 'mailing_address' in form:
        if ('&' in form['mailing_address']):
            form['mailing_address'] = form['mailing_address'].replace('&','and')
            
    #covert : symbol in address, because rocky doesn't like them and people use
    if 'mailing_address' in form:
        if (':' in form['mailing_address']):
            form['mailing_address'] = form['mailing_address'].replace(':',' ')
    
    #covert ' symbol in address, because rocky doesn't like them and people use
    if 'mailing_address' in form:
        if ('\'' in form['mailing_address']):
            form['mailing_address'] = form['mailing_address'].replace('\'','')
    
    #covert , symbol in address, because rocky doesn't like them and people use
    if 'mailing_address' in form:
        if (',' in form['mailing_address']):
            form['mailing_address'] = form['mailing_address'].replace(',','')
    
    #covert + symbol in address, because rocky doesn't like them and people use
    if 'mailing_address' in form:
        if ('+' in form['mailing_address']):
            form['mailing_address'] = form['mailing_address'].replace('+',' ')
            
    #covert & symbol in address, because rocky doesn't like them and people use
    if 'prev_address' in form:
        if ('&' in form['prev_address']):
            form['prev_address'] = form['prev_address'].replace('&','and')
            
    #covert : symbol in address, because rocky doesn't like them and people use
    if 'prev_address' in form:
        if (':' in form['prev_address']):
            form['prev_address'] = form['prev_address'].replace(':',' ')
    
    #covert ' symbol in address, because rocky doesn't like them and people use
    if 'prev_address' in form:
        if ('\'' in form['prev_address']):
            form['prev_address'] = form['prev_address'].replace('\'','')
    
    #covert , symbol in address, because rocky doesn't like them and people use
    if 'prev_address' in form:
        if (',' in form['prev_address']):
            form['prev_address'] = form['prev_address'].replace(',','')
    
    #covert + symbol in address, because rocky doesn't like them and people use
    if 'prev_address' in form:
        if ('+' in form['prev_address']):
            form['prev_address'] = form['prev_address'].replace('+',' ')

    #rocky api only accepts en/es/ko/zh, clear country specific locales
    if 'lang' in form:
        lang = form.get('lang')
        if lang.startswith('en'):
            lang = 'en'
        elif lang.startswith('es'):
            lang = 'es'
        elif lang.startswith('ko'):
            lang = 'ko'
        elif lang.startswith('zh'):
            lang = 'zh'
        elif lang.startswith('zh-TW'):
            lang = 'zh-TW'
        elif lang.startswith('tl'):
            lang = 'tl'
        elif lang.startswith('ilo'):
            lang = 'ilo'
        elif lang.startswith('bn'):
            lang = 'bn'
        elif lang.startswith('ur'):
            lang = 'ur'
        elif lang.startswith('vi'):
            lang = 'vi'
        elif lang.startswith('th'):
            lang = 'th'
        elif lang.startswith('hi'):
            lang = 'hi'
        else:
            lang = 'en'
        form['lang'] = lang

    return form

def get_branding(context):
    """Util method to get branding given partner id.
    Used in submit view, because we need access before the context processor runs.
    Not totally DRY, but better than faking an HttpRequest."""

    #check for cobrand form first
    try:
        context['cobrandform'] = CoBrandForm.objects.get(partner_id=context['partner'])
        context['customform'] = context['cobrandform'].toplevel_org
        return context
    except (CoBrandForm.DoesNotExist,ValueError):
        pass

    #then custom form
    context['cobrandform'] = None
    try:
        context['customform'] = CustomForm.objects.get(partner_id=context['partner'])
        return context
    except (CustomForm.DoesNotExist,ValueError):
        pass

    #finally, try rtv whitelabel
    try:
        #check cache first
        cache_key = 'rtv_whitelabel_%s' % context['partner']
        if cache.get(cache_key):
            rtv_whitelabel = cache.get(cache_key)
        else:
            rtv_whitelabel = rtv_proxy('GET',{'partner_id':context['partner']},
            'api/v3/partnerpublicprofiles/partner.json')
            cache.set(cache_key,rtv_whitelabel,1) #cache whitelabel hits for 3600 a bit
    
        #duck type a customform
        quack = {'partner_id':context['partner'],
                 'name':rtv_whitelabel['org_name'],
                 'logo':rtv_whitelabel['logo_image_URL'],
                 'logo_link':rtv_whitelabel['org_URL'],
                 'show_sms_box':rtv_whitelabel['partner_ask_sms_opt_in'],
                 'show_volunteer_box':rtv_whitelabel['rtv_ask_volunteer'],
                 }
        if context['language'] == "es":
            quack['question_1'] = rtv_whitelabel['survey_question_1_es']
            quack['question_2'] = rtv_whitelabel['survey_question_2_es']
        elif context['language'] == "ko":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ko']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ko']
        elif context['language'] == "zh":
            quack['question_1'] = rtv_whitelabel['survey_question_1_zh']
            quack['question_2'] = rtv_whitelabel['survey_question_2_zh']
        elif context['language'] == "zh-TW":
            quack['question_1'] = rtv_whitelabel['survey_question_1_zh-TW']
            quack['question_2'] = rtv_whitelabel['survey_question_2_zh-TW']
        elif context['language'] == "tl":
            quack['question_1'] = rtv_whitelabel['survey_question_1_tl']
            quack['question_2'] = rtv_whitelabel['survey_question_2_tl']
        elif context['language'] == "ilo":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ilo']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ilo']
        elif context['language'] == "bn":
            quack['question_1'] = rtv_whitelabel['survey_question_1_bn']
            quack['question_2'] = rtv_whitelabel['survey_question_2_bn']
        elif context['language'] == "ur":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ur']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ur']
        elif context['language'] == "vi":
            quack['question_1'] = rtv_whitelabel['survey_question_1_vi']
            quack['question_2'] = rtv_whitelabel['survey_question_2_vi']
        elif context['language'] == "th":
            quack['question_1'] = rtv_whitelabel['survey_question_1_th']
            quack['question_2'] = rtv_whitelabel['survey_question_2_th']
        elif context['language'] == "hi":
            quack['question_1'] = rtv_whitelabel['survey_question_1_hi']
            quack['question_2'] = rtv_whitelabel['survey_question_2_hi']
        else:
            quack['question_1'] = rtv_whitelabel['survey_question_1_en']
            quack['question_2'] = rtv_whitelabel['survey_question_2_en']

        #check for missing logo image url
        if '/logos/original/missing.png' in quack['logo']:
            quack['logo'] = None
        context['rtv_whitelabel'] = True

        #unlike in context_processor, this needs to be object-like
        #so create a CustomForm, but don't save it
        fakin_bacon = CustomForm(**quack)
        context['customform'] = fakin_bacon
    except KeyError:
        #whitelabel error
        logger.error("white label error, id %s" % context['partner'],
            exc_info=True,extra={'context':context})

    return context

def empty(the_list):
    #returns True if list has only one object, and it's empty or otherwise False-y
    #need this because the form is a dict of lists, not a dict of values
    #could be as simple as not bool(the_list[0]), but let's be more explicit...
    if len(the_list) == 0:
        return True
    try:
        elem = the_list[0]
        if bool(elem):
            return False
        else:
            return True
    except IndexError:
        return False

def removeNonAscii(s):
    return "".join(i for i in s if ord(i)<128)
