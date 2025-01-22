// md5 
function md5(timestamp) {
    const secret_key=os.environ['SECRET_KEY'];
    const crypto = require('crypto');
    const hash = crypto.createHash('md5');
    hash.update(secret_key + timestamp);
    return hash.digest('hex');
}
// token format: auth:timestamp
function isValidToken(str) {
    const super_token=os.environ['SUPER_TOKEN'];
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
let timestamp1 = Date.now() - 0 + '';
console.log(timestamp1);
let auth = md5(timestamp1);
let token = timestamp1 + ':' + auth;
console.log('token: ' + token);
console.log(isValidToken(token));