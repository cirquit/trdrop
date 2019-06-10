//.pragma library

// windows and linux conform, see https://stackoverflow.com/questions/24927850/get-the-path-from-a-qml-url
function urlToPath(urlString) {
    var s
    if (urlString.startsWith("file:///")) {
        var k = urlString.charAt(9) === ':' ? 8 : 7
        s = urlString.substring(k)
    } else {
        s = urlString
    }
    return decodeURIComponent(s);
}

// value is to be round, decimal places has the natural number domain (0, 1,..)
function round(value, decimalPlaces) {
    var factor = Math.pow(10.0, decimalPlaces);
    return Math.round(value * factor) / factor;
}


