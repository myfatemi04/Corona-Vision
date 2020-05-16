"use strict";
exports.__esModule = true;
function utc_iso(date) {
    if (typeof date == "undefined") {
        return utc_iso(new Date());
    }
    if (typeof date == "string") {
        return date;
    }
    var year = date.getUTCFullYear();
    var month = "" + (date.getUTCMonth() + 1);
    var day = "" + date.getUTCDate();
    month = month.padStart(2, "0");
    day = day.padStart(2, "0");
    return year + "-" + month + "-" + day;
}
exports.utc_iso = utc_iso;
