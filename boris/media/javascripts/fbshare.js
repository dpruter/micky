var fbAppID="347566241989371",fbAppUrl="https://apps.facebook.com/rockthevotenow/";function getParam(a){a=a.replace(/[\[]/,"\\[").replace(/[\]]/,"\\]");a=RegExp("[\\?&]"+a+"=([^&#]*)").exec(window.location.search);return a===null?"":decodeURIComponent(a[1].replace(/\+/g," "))}window.fbAsyncInit=function(){FB.init({appId:fbAppID,status:true,cookie:true,xfbml:true});FB.Canvas.setAutoGrow()};
$("a.button.facebook#facebook-app-share").click(function(){$b=$(this);var a="?partner=";a+=getParam("partner")!=""?getParam("partner"):"19093";FB.ui({method:"stream.publish",attachment:{name:"Rock the Vote",description:"Register to vote in 3 easy steps using Rock the Vote's online voter registration tool!",message:"Have you registered to vote?",media:[{type:"flash",swfsrc:"https://"+window.location.hostname+"/static/widgetloader/rtv_fb.swf"+a,imgsrc:"https://"+window.location.hostname+"/static/images/flash-preview.gif",
width:"130",height:"87",expanded_width:"398",expanded_height:"375"}],href:"https://register2.rockthevote.com/"+a},user_message_prompt:"Tell your friends to register!"},function(b){b.hasOwnProperty("post_id")?$b.html("Invite Your Friends!").unbind("click").click(function(){FB.ui({method:"apprequests",message:"Become a registered voter!"},function(c){c.hasOwnProperty("request")?$b.html("Thanks for sharing!").attr("disabled",true).css("opacity",0.4).unbind("click"):alert("There was an error in sending your requests. Please try again.")})}):
alert("There was an error in publishing your post. Please try again.")})});(function(a){var b=a.getElementsByTagName("script")[0];if(!a.getElementById("facebook-jssdk")){a=a.createElement("script");a.id="facebook-jssdk";a.async=true;a.src="//connect.facebook.net/en_US/all.js";b.parentNode.insertBefore(a,b)}})(document);