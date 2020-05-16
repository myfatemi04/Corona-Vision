"use strict";
exports.__esModule = true;
function getLabel(country, province, county) {
    var label = "World";
    if (!country)
        return label;
    label = country;
    if (!province)
        return label;
    label = province + ", " + label;
    if (!county)
        return label;
    label = county + ", " + label;
    return label;
}
exports.getLabel = getLabel;
function getChildLabel(country, province, county) {
    if (!country)
        return "country";
    if (!province)
        return "province";
    if (!county)
        return "county";
}
exports.getChildLabel = getChildLabel;
