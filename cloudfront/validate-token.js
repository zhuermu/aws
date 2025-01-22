function handler(event) {
    var request = event.request;
    var cookies = request.cookies;
    
    // First check if auth cookie exists
    if (cookies && cookies.auth) {
        var authCookie = cookies.auth;
        if (authCookie && isValidToken(cookies.auth.value)) {
            return request;
        }
    }

    // If no valid cookie, check if this is a login request with token
    var querystring = request.querystring;
    if (querystring.tmptoken) {
        var token = querystring.tmptoken.value;
        
        if (isValidToken(token)) {
            // Create response with cookie and redirect
            var response = {
                statusCode: 302,
                statusDescription: 'Found',
                headers: {
                    'location': {
                        value: '/'
                    }
                },
                cookies: {
                    'auth': {
                        value: token,
                        attributes: 'Max-Age=3600; Path=/; Secure; HttpOnly'
                    }
                }
            };
            return response;
        }
    }

    // If no valid cookie or token, return forbidden
    return {
        statusCode: 403,
        statusDescription: 'Forbidden',
        body: 'Invalid token'
    };

    function md5(timestamp) {
        const secret_key="${SECRET_KEY: replace me}";
        const crypto = require('crypto');
        const hash = crypto.createHash('md5');
        hash.update(secret_key + timestamp);
        return hash.digest('hex');
    }
    // token format: auth:timestamp
    function isValidToken(str) {
        const super_token="${SUPER_TOKEN: replace me}";
        if (str === super_token) {
            return true;
        }
        if (str.indexOf(":") <= 0) {
            return false;
        }
        let timestampStr = str.split(":")[0];
        let auth = str.split(":")[1];
        const timestamp = parseInt(timestampStr);
        const now = Date.now();
        if (isNaN(timestamp) || now - timestamp > 3600000) {
            console.log('timeout')
            return false;
        }
        return md5(timestamp) === auth;
    }
}
