const login_button = document.getElementById('login');
const logout_button = document.getElementById('logout');
const storage = window.localStorage;
const recentAlerts = document.getElementById('recent-alerts');

var get_active_jwt = function() {
	var active_jwt = '';
	try {
		active_jwt = storage.getItem('jwt');
	}
	catch (error){}
	return active_jwt
};

var getRecentAlerts = function(ACTIVE_JWT) {
	console.log(ACTIVE_JWT);
	var response = {};
	var request = new Request('/recent_alerts', {
		headers: {'Authorization': 'Bearer ' + ACTIVE_JWT}
	});
	fetch(request)
	.then(response => response.json())
	.then(jsonResponse => {
		console.log(jsonResponse);
		response = jsonResponse;
	})
	.catch(function(e) {
		console.error(e.message);
	});	
	return response;
};

var hide_login = function() {
	login_button.className = 'hidden';
	logout_button.className = '';
};

var hide_logout = function() {
	logout_button.className = 'hidden';
	login_button.className = '';
};

var show_recent_alerts = function(jsonResponse) {
	recentAlerts.className = '';
	if (jsonResponse['alerts'].length === 0) {
		recentAlerts.innerHTML = '<p>Your recently added alerts will appear here</p>';
	}
	else {
		for (let i = 0 ; i < jsonResponse['alerts'].length ; i++) {
			let alert = jsonResponse['alerts'][i];
			let alert_div = '';
			alert_div+= '<div data-id= "' + alert['alert_id'] + '">';
			alert_div+= '<p>' + alert['store'] + '</p>';
			alert_div+= '<p>' + alert['product_name'] + '<a>' + alert['product_link'] + '</a>' + '</p>';
			alert_div+= '<p><img src="' + alert['product_image'] + '"></p>';
			alert_div+= '<p>Price: ' + alert['price'] + '<p/>';
			alert_div+= '<p>Difference in price: ' + alert['price_difference'] + '<p/>';
			alert_div+= '</div>';
			recentAlerts.innerHTML+= alert_div; 
		}
	}
};

document.addEventListener("DOMContentLoaded", function (event) {
	console.log('Content loaded');
	const ACTIVE_JWT = get_active_jwt();
	// If the token has not yet expired:
	// request user recent alerts and profile
	if (ACTIVE_JWT) {
		console.log( 'Valid jwt on loading: ' + ACTIVE_JWT);
		var response = getRecentAlerts(ACTIVE_JWT);
		hide_login();
		// parse response and show recent_alerts div
		show_recent_alerts(response);
	}	
});

var get_token = function() {
	console.log('Inside get_token')
	var hash = window.location.hash;
	var token = hash.substring(
		hash.indexOf('=') + 1, 
		hash.indexOf('&')
	);
	console.log(token);
	document.write(token);
	return token;
};

var login = function(event) {
	console.log('Inside login');
	const domain = 'fs-webdev.eu.auth0.com';
	const audience = 'price_tracker';
	const clientID = 'qfecxJQCicccSMa1KSVM8I6VP85NrYHV';
	const callbackURL = 'http://localhost:5000/';
	const scope = 'openid%20profile%20email';

	var auth0Client = new auth0.WebAuth({
	    clientID: clientID,
	    domain: domain,
	    audience: audience,
	    redirectUri: callbackURL,
	    responseType: 'token',
	    scope: scope
    });
    auth0Client.authorize();
    console.log('auth request sent');
    auth0Client.crossOriginVerification();
    console.log('Token received');
    var token = get_token();
    console.log(token);
	storage.setItem('jwt', token);
	var response = getRecentAlerts(token);
	hide_login();
	show_recent_alerts();
};

login_button.onclick = login;

var logout = function() {
	storage.removeItem('jwt');
	hide_logout();
	recentAlerts.className = 'hidden';
	recentAlerts.innerHTML = '';
};

logout_button.onclick = logout;

 //    auth0Client.parseHash({ hash: window.location.hash }, function(err, authResult) {
 //    	console.log(hash);
	// 	if (err) {
	// 	return console.log(err);
	// 	}

	// 	// The contents of authResult depend on which authentication parameters were used.
	// 	// It can include the following:
	// 	// authResult.accessToken - access token for the API specified by `audience`
	// 	// authResult.expiresIn - string with the access token's expiration time in seconds
	// 	// authResult.idToken - ID token JWT containing user profile information

	// 	auth0Client.userInfo(authResult.accessToken, function(err, user) {
	// 		// Now you have the user's information
	// 		console.log(user.email);
	// 	});
	// });
