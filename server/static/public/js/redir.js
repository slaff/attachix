/* 
 * Simple redirector for JavaScript enabled clients
 */
var p =  0;
var path = location.pathname;
path = path.replace(/(\/{2,})/,'/');
var host = location.hostname;

if (host == 't.attachix.de') {
    p = 2;
    var parts = path.split('/')
    parts.shift()
    if (p > parts.length) {
        p = parts.length
    }

    var baseUri = ''
    for(var i=0; i<p; i++) {
        baseUri += '/' + parts.shift()
    }

    path = '/'+parts.join('/')

    location.replace(location.protocol+'//'+location.host+'/~js/index.html?baseURL='+baseUri+'#files'+path)
}
else {
    location.replace(location.protocol+'//'+location.host+'/~js/index.html#files'+path)
}