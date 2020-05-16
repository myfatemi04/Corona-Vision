"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
var util_1 = require("./util");
var labels_1 = require("./labels");
var corona_sql = require("./corona_sql");
var url = require("url");
var stateNames = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming"
];
var mapTree = {
    'World': [
        'Argentina',
        'Australia',
        'Canada',
        'India',
        'Italy',
        'Japan',
        'Netherlands',
        'Portugal',
        'South Korea',
        'Spain',
        'United States',
    ],
    'United States': stateNames
};
var countryMap = function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var country, province, label, dates;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                country = req.params.country || '';
                province = req.params.province || '';
                if (country.toLowerCase() == 'world') {
                    country = '';
                }
                label = labels_1.getLabel(country, province);
                return [4 /*yield*/, corona_sql.getDates(country, province, "", "childRequired")];
            case 1:
                dates = _a.sent();
                res.render("maps/country", {
                    country: country,
                    province: province,
                    entryDates: dates,
                    relatedMaps: mapTree[label],
                    label: label
                });
                return [2 /*return*/];
        }
    });
}); };
exports.countryMap = countryMap;
var mapDataAPI = function (req, res) {
    var params = url.parse(req.url, true).query;
    var date = params.date || util_1.utc_iso(new Date());
    var country = params.country || '';
    var province = params.province || '';
    if (country == 'world')
        country = '';
    corona_sql.getDatapointChildren(date, country, province, '').then(function (results) {
        var resultsJSON = {
            subregions: {},
            overall: {}
        };
        var childLabel = labels_1.getChildLabel(country, province);
        for (var _i = 0, results_1 = results; _i < results_1.length; _i++) {
            var result = results_1[_i];
            if (result[childLabel]) {
                resultsJSON.subregions[result[childLabel]] = result;
            }
            else {
                resultsJSON.overall = result;
            }
        }
        res.json(resultsJSON);
    });
};
exports.mapDataAPI = mapDataAPI;
/* Heatmap API - returns a list of lat/longs, and various properties. */
var heatmapAPI = function (req, res) {
    var entryDate = req.query['date'] || util_1.utc_iso(new Date());
    corona_sql.getHeatmap(entryDate).then(function (heatmapData) {
        res.json(heatmapData);
    });
};
exports.heatmapAPI = heatmapAPI;
