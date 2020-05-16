"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
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
var corona_sql = require("./corona_sql");
var util_1 = require("./util");
var url = require("url");
/* Totals API
 * This provides results for a given country, province, or county */
var totalsAPI = function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, country, province, county, entryDate;
    return __generator(this, function (_a) {
        params = req.query;
        country = params.country || "";
        province = params.province || "";
        county = params.county || "";
        entryDate = params.date || util_1.utc_iso(new Date());
        corona_sql.getDatapointChildren(entryDate, country, province, county).then(function (content) { return res.send(JSON.stringify(content)); });
        return [2 /*return*/];
    });
}); };
exports.totalsAPI = totalsAPI;
/* Totals Sequence API
 * Gives the most recent data, with missing dates filled in */
var totalsSequenceAPI = function (req, res) {
    var params = req.query;
    // get location and date
    var country = params.country || "";
    var province = params.province || "";
    var county = params.county || "";
    corona_sql.getDatapointSequence(country, province, county).then(function (content) {
        var labels = ['total', 'recovered', 'deaths'];
        var resp = {
            entry_date: [],
            total: [],
            recovered: [],
            deaths: []
        };
        for (var _i = 0, labels_1 = labels; _i < labels_1.length; _i++) {
            var label = labels_1[_i];
            resp[label] = [];
        }
        if (content.length == 0) {
            res.json(__assign({}, resp));
            return;
        }
        /* !!! This strongly relies on the date format !!! */
        var day = new Date(content[0].entry_date);
        var last_day = new Date(content[content.length - 1].entry_date);
        var i = 0;
        // <, NOT <=, because the most recent day's data is incomplete
        while (day < last_day) {
            resp.entry_date.push(util_1.utc_iso(day));
            for (var _a = 0, labels_2 = labels; _a < labels_2.length; _a++) {
                var label = labels_2[_a];
                resp[label].push(content[i][label]);
            }
            // we don't increment the data index if the next date isn't found
            day.setUTCDate(day.getUTCDate() + 1);
            if (i + 1 < content.length) {
                var content_iso = util_1.utc_iso(new Date(content[i + 1].entry_date));
                if (util_1.utc_iso(day) == content_iso)
                    i += 1;
            }
        }
        for (var _b = 0, labels_3 = labels; _b < labels_3.length; _b++) {
            var label = labels_3[_b];
            var daily_label = "d" + label;
            var last_val = 0;
            resp[daily_label] = [];
            for (var i_1 = 0; i_1 < resp[label].length; i_1++) {
                var this_val = resp[label][i_1];
                resp[daily_label].push(this_val - last_val);
                last_val = this_val;
            }
        }
        res.json(resp);
    });
};
exports.totalsSequenceAPI = totalsSequenceAPI;
/* Countries API - returns a list of all countries for a given date */
var countriesAPI = function (req, res) {
    var params = url.parse(req.url, true).query;
    var entryDate = params.date || util_1.utc_iso(new Date());
    corona_sql.getCountries(entryDate).then(function (content) {
        res.json(content);
    });
};
exports.countriesAPI = countriesAPI;
/* Provinces API - gives a list of provinces for a given country and date */
var provincesAPI = function (req, res) {
    var params = url.parse(req.url, true).query;
    var entryDate = params.date || util_1.utc_iso(new Date());
    var country = params.country || "";
    corona_sql.getProvinces(entryDate, country).then(function (content) { return res.json(content); });
};
exports.provincesAPI = provincesAPI;
/* County API - gives a list of counties for a given country, province, and date */
var countiesAPI = function (req, res) {
    var params = url.parse(req.url, true).query;
    var entryDate = params.date || util_1.utc_iso(new Date());
    var country = params.country || "";
    var province = params.province || "";
    corona_sql.getCounties(entryDate, country, province).then(function (content) { return res.json(content); });
};
exports.countiesAPI = countiesAPI;
/* Dates API - list all dates that we have on record */
var listDates = function (req, res) {
    var params = url.parse(req.url, true).query;
    var country = params.country || "";
    var province = params.province || "";
    var county = params.county || "";
    corona_sql.getDates(country, province, county).then(function (content) { return res.json(content); });
};
exports.listDates = listDates;
/* Cases-by-date API - returns all cases (with a labelled location) for a given date. Used by the map */
var dateCasesAPI = function (req, res) {
    var params = url.parse(req.url, true).query;
    var date = params.date || util_1.utc_iso(new Date());
    corona_sql.getHeatmap(date).then(function (content) { return res.json(content); });
};
exports.dateCasesAPI = dateCasesAPI;
