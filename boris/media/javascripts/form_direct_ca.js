function showStateRegContinueButtons() {
  if ($("input#registrant_has_state_license_1:checked").val()=='1') {
      $('.has_no_license').hide();
      $('.has_license').show();
  } else {
      $('.has_no_license').hide();
      $('.has_license').show();
  }
}

function redirectToRegularForm() {
   //serialize values input so far
  var formValues = $('form input[name!=csrfmiddlewaretoken], form select').serialize();
  //redirect to regular form
  var state = $('form.registration-form input#home_state_id').val();
  window.location.replace('/registrants/new/?state='+state+'&no_redirect=1&'+formValues);
}

function submitPartialToRocky() {
  //submit partial registration to RTV for tracking
  var formValues = $('form.registration-form').serialize();
  var submitURL = $('form.registration-form').attr('action');
  //window.location.replace(submitURL+'?'+formValues);
  $.ajax({
    type:'POST',
    url:submitURL,
    data: formValues,
    success: continueToStateForm
  });
}

function continueToStateForm(data, textStatus, xhr) {
  //hide initial form
  $('form.registration-form').hide();

  //show state explanation
  $('.explanation#state').show();
  
  //function defined in template, so we can reuse this file for multiple states
  add_state_iframe(data);
  
  //add tracking pixel for floodlight
  //addFloodlightTrackingPixel();
  
  //show share buttons
  $('body').addClass('finish');
  $('.share').show();
  $('#share-link').hide();
}

$(document).ready(function() {
  $('.has_license').hide();

  showStateRegContinueButtons();
  $('#registrant_has_state_license_1, #registrant_has_state_license_0').click(showStateRegContinueButtons);

  $('form.registration-form').submit(function(event) {
    event.preventDefault(); //don't actually submit the form

    if ($("input#registrant_has_state_license_1:checked").val()=='1') {
      	submitPartialToRocky();
    } else {
       submitPartialToRocky();
    }

  });
});