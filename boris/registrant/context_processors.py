from proxy.models import CustomForm,CoBrandForm
from proxy.views import rtv_proxy
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def facebook(request):
    """Context processor to add facebook partner & source from session"""
    context = {}
    
    if request.session.has_key('facebook_canvas'):
        if request.session.has_key('facebook_partner_id'):
            context['partner'] = request.session['facebook_partner_id']
        elif not request.GET.has_key('partner'):
            #use facebook default
            context['partner'] = 19093

        #if not already a source, add it
        if not request.GET.get('source') and request.session.has_key('facebook_source'):
            context['source'] = request.session['facebook_source']

    return context

def whitelabel(request):
    """
    Context processor to add customform and cobrandform to request.session
    Checks proxy CoBrandForm, then CustomForm, then rocky whitelabel API
    """
    context = {}

    #save partner
    if request.GET.get('partner'):
        partner = request.GET.get('partner')
        context['partner'] = partner
        context['has_partner'] = True
    elif not context.has_key('partner'):
        #no partner specified, return early
        context['partner'] = 1
        context['has_partner'] = False
        return context

    #get whitelabel branding
    #try CoBrandForm first
    try:
        cobrand = CoBrandForm.objects.get(partner_id=partner)
        context['cobrandform'] = cobrand
        context['customform'] = cobrand.toplevel_org
        return context
    except (CoBrandForm.DoesNotExist,ValueError):
        pass

    #no CoBrandForm, try CustomForm
    context['cobrandform'] = None
    try:
        context['customform'] = CustomForm.objects.get(partner_id=partner)
        return context
    except (CustomForm.DoesNotExist,ValueError):
        context['customform'] = None

    try:
        #finally, try rtv whitelabel

        #check cache first
        cache_key = 'rtv_whitelabel_%s' % context['partner']
        if cache.get(cache_key):
            rtv_whitelabel = cache.get(cache_key)
        else:
            rtv_whitelabel = rtv_proxy('GET',{'partner_id':context['partner']},
            'api/v3/partnerpublicprofiles/partner.json')
            cache.set(cache_key,rtv_whitelabel,3600) #cache whitelabel hits for an hour
            #set back to 3600 when done testing
    
        #duck type a customform
        quack = {'partner_id':context['partner'],
                     'name':rtv_whitelabel['org_name'],
                     'logo':rtv_whitelabel['logo_image_URL'],
                     'logo_link':rtv_whitelabel['org_URL']}
        if rtv_whitelabel['whitelabeled']:
            quack['show_sms_box'] = rtv_whitelabel['partner_ask_sms_opt_in']
            quack['show_volunteer_box'] = rtv_whitelabel['partner_ask_volunteer']
            quack['show_email_optin'] = rtv_whitelabel['partner_ask_email_opt_in']
            quack['show_rtvemail_optin'] = rtv_whitelabel['rtv_ask_email_opt_in']
            quack['show_rtvsms_box'] = rtv_whitelabel['rtv_ask_sms_opt_in']
        else:
            quack['show_sms_box'] = rtv_whitelabel['rtv_ask_sms_opt_in']
            quack['show_volunteer_box'] = rtv_whitelabel['rtv_ask_volunteer']
            quack['show_email_optin'] = rtv_whitelabel['rtv_ask_email_opt_in']
            
        if request.LANGUAGE_CODE == "es":
            quack['question_1'] = rtv_whitelabel['survey_question_1_es']
            quack['question_2'] = rtv_whitelabel['survey_question_2_es']
        elif request.LANGUAGE_CODE == "ko":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ko']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ko']
        elif request.LANGUAGE_CODE == "zh":
            quack['question_1'] = rtv_whitelabel['survey_question_1_zh']
            quack['question_2'] = rtv_whitelabel['survey_question_2_zh']
        elif request.LANGUAGE_CODE == "zh-TW":
            quack['question_1'] = rtv_whitelabel['survey_question_1_zh-tw']
            quack['question_2'] = rtv_whitelabel['survey_question_2_zh-tw']
        elif request.LANGUAGE_CODE == "hi":
            quack['question_1'] = rtv_whitelabel['survey_question_1_hi']
            quack['question_2'] = rtv_whitelabel['survey_question_2_hi']
        elif request.LANGUAGE_CODE == "th":
            quack['question_1'] = rtv_whitelabel['survey_question_1_th']
            quack['question_2'] = rtv_whitelabel['survey_question_2_th']
        elif request.LANGUAGE_CODE == "vi":
            quack['question_1'] = rtv_whitelabel['survey_question_1_vi']
            quack['question_2'] = rtv_whitelabel['survey_question_2_vi']
        elif request.LANGUAGE_CODE == "ur":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ur']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ur']
        elif request.LANGUAGE_CODE == "bn":
            quack['question_1'] = rtv_whitelabel['survey_question_1_bn']
            quack['question_2'] = rtv_whitelabel['survey_question_2_bn']
        elif request.LANGUAGE_CODE == "ilo":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ilo']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ilo']
        elif request.LANGUAGE_CODE == "tl":
            quack['question_1'] = rtv_whitelabel['survey_question_1_tl']
            quack['question_2'] = rtv_whitelabel['survey_question_2_tl']
        elif request.LANGUAGE_CODE == "ur":
            quack['question_1'] = rtv_whitelabel['survey_question_1_ur']
            quack['question_2'] = rtv_whitelabel['survey_question_2_ur']
        else:
            quack['question_1'] = rtv_whitelabel['survey_question_1_en']
            quack['question_2'] = rtv_whitelabel['survey_question_2_en']

        #check for missing logo image url
        if '/logos/original/missing.png' in quack['logo']:
            quack['logo'] = None
        context['rtv_whitelabel'] = True
        context['customform'] = quack

    except KeyError,e:
        #whitelabel error
        logger.error("white label error %s, id %s" % (e,context['partner']),
            exc_info=True,extra={'request':request})
    
    return context

def source(request):
    source = None
    if 'source' in request.session:
        #it's been reset by the middleware
        source = request.session['source']
    elif request.GET.get('source'):
        source = request.GET.get('source')
    context = {'source':source}
    return context