
function setCookie(cname, cvalue, exdays) {
  // A function to set cookie from document.cookie
  // https://www.w3schools.com/js/js_cookies.asp
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  // A function to get cookie from document.cookie
  // https://www.w3schools.com/js/js_cookies.asp
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}


function checkCookiesEnabledShowConsent(){
  /* Check if cookie consent has been accepted,
      if not, request the user for a consent
  */
  if (getCookie("saas-fun") == "" && getCookie("saas-cookie-consent-accepted") == ""
      ) {
      console.log("Cookie consent has not been accepted")
      // means cookie is not set yet!

      // add onclick event listener to setCookie cookie accepted
      $('#cookie-consent-accept-btn').click(function(evt) {
        setCookie("saas-cookie-consent-accepted", "true", 30)
      });

      // ask the user for permission
      $('#cookieModal').modal('show');
      return false
  } else {
      console.log("Cookie consent has already been accepted.")
      return true
  }
}

function restoreConfigurationOnLoad() {
  /* Restores the configuration as set in cookies */
  // check if a cookie is set to true
    if ( getCookie("saas-fun") == "true" ) {
      // restore the saved cookie
      console.log("Restoring configuration from cookie")
      $('#funCheckBox').prop('checked', true);
      enableFunGradientBackground();

    } else {
        $('#funCheckBox').prop('checked', false);  // ignore entropy
        // show cookie consent; if necessary
        checkCookiesEnabledShowConsent();

    }
  }
}

function enableFunGradientBackground(){
  console.log("Enabling fun gradient background animation.");
  $("body").addClass("fun-gradient-animation-bg");
  setCookie("saas-fun", "true", 365);
}

function disableFunGradientBackground() {
  console.log("Disabling fun gradient background animation");
  $("body").removeClass("fun-gradient-animation-bg");
  setCookie("saas-fun", "false", 365);
}

}