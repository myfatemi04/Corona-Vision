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
require("./interfaces");
var corona_sql = require("./corona_sql");
var express = require("express");
var path = require("path");
var util_1 = require("./util");
var labels_1 = require("./labels");
var fs = require('fs');
var url = require('url');
var Handlebars = require('hbs');
var COLORS = require("./colors.js");
var datatables = require('./datatables');
function registerPartials() {
    /* Register the "partials" - handlebars templates that can be included in other templates */
    Handlebars.registerPartial("coronavisionNavbar", fs.readFileSync(path.join(__dirname, "views/navbar.hbs"), "utf-8"));
    Handlebars.registerPartial("coronavisionStyles", fs.readFileSync(path.join(__dirname, "views/styles.hbs"), "utf-8"));
    Handlebars.registerHelper('ifeq', function (a, b, options) {
        if (a == b) {
            return options.fn(this);
        }
        return options.inverse(this);
    });
    Handlebars.registerHelper('percent', function (a, b) {
        return (100 * a / b).toFixed(2) + "%";
    });
    Handlebars.registerHelper('pos', function (conditional, options) {
        if (conditional > 0) {
            return options.fn(this);
        }
        else {
            return options.inverse(this);
        }
    });
}
exports.registerPartials = registerPartials;
var api_1 = require("./api");
var news_1 = require("./news");
var maps_1 = require("./maps");
function getRouter() {
    var router = express.Router();
    router.get('/', mainPage);
    router.get('/calculated', function (req, res) { return res.render("calculated"); });
    router.get('/charts/info', function (req, res) { return res.render("charts/info"); });
    router.get('/future', chartsPage);
    router.get("/cases/totals", api_1.totalsAPI);
    router.get("/cases/totals_sequence", api_1.totalsSequenceAPI);
    router.get("/cases/date", api_1.dateCasesAPI);
    router.get("/list/dates", api_1.listDates);
    router.get("/api/countries", api_1.countriesAPI);
    router.get("/api/countrieswithstates", api_1.countriesWithStatesAPI);
    router.get("/api/provinces", api_1.provincesAPI);
    router.get("/api/counties", api_1.countiesAPI);
    router.get("/api/mapdata", maps_1.mapDataAPI);
    router.get("/api/heatmap", maps_1.heatmapAPI);
    router.get('/maps/circle', function (req, res) { return res.render("maps/circle"); });
    router.get('/maps/heat', function (req, res) { return res.render("maps/heat"); });
    router.get("/maps/", maps_1.countryMap);
    router.get("/maps/:country", maps_1.countryMap);
    router.get("/maps/:country/:province", maps_1.countryMap);
    router.get("/news", news_1.getNews);
    router.get("/howtohelp", function (req, res) { return res.render("details/howtohelp"); });
    router.get("/contact", function (req, res) { return res.render("details/contact"); });
    router.get("/sources", function (req, res) { return res.render("details/sources"); });
    router.get("/statisticsInfo", function (req, res) { return res.render("details/statisticsInfo"); });
    router.get("/simulate/curve", function (req, res) { return res.render("simulate_curve"); });
    return router;
}
exports.getRouter = getRouter;
var mainPage = function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, country, province, county, entry_date, label, data, lastUpdate, mainDatapoint, _i, data_1, datapoint, dates, firstDay, lastDay, countries, provinces, counties, todayStr;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                country = params.country || "";
                province = params.province || "";
                county = params.county || "";
                entry_date = params.date || util_1.utc_iso(new Date());
                label = labels_1.getLabel(country, province, county);
                return [4 /*yield*/, corona_sql.getDatapointChildren(entry_date, country, province, county)];
            case 1:
                data = _a.sent();
                if (!data) {
                    res.render("error", { error: "Location not found" });
                    return [2 /*return*/];
                }
                lastUpdate = new Date(Math.max.apply(Math, data.map(function (x) { return x.update_time.getTime(); })));
                for (_i = 0, data_1 = data; _i < data_1.length; _i++) {
                    datapoint = data_1[_i];
                    if (datapoint.country == country && datapoint.province == province && datapoint.county == county) {
                        mainDatapoint = datapoint;
                        break;
                    }
                }
                return [4 /*yield*/, corona_sql.getDates(country, province, county)];
            case 2:
                dates = _a.sent();
                firstDay = dates[dates.length - 1];
                lastDay = dates[0];
                countries = [];
                provinces = [];
                counties = [];
                todayStr = entry_date;
                return [4 /*yield*/, corona_sql.getCountries(todayStr)];
            case 3:
                countries = _a.sent();
                if (!country) return [3 /*break*/, 5];
                return [4 /*yield*/, corona_sql.getProvinces(todayStr, country)];
            case 4:
                provinces = _a.sent();
                _a.label = 5;
            case 5:
                if (!province) return [3 /*break*/, 7];
                return [4 /*yield*/, corona_sql.getCounties(todayStr, country, province)];
            case 6:
                counties = _a.sent();
                _a.label = 7;
            case 7:
                res.render("main_page", __assign(__assign({}, datatables.make_rows(data, country, province, county, entry_date)), { last_update: datatables.format_update_time(lastUpdate), mainDatapoint: mainDatapoint, country: country, province: province, county: county, entry_date: entry_date, label: label, dates: dates, isLast: (lastDay == entry_date), isFirst: (firstDay == entry_date), countries: countries, provinces: provinces, counties: counties, COLORS: COLORS }));
                return [2 /*return*/];
        }
    });
}); };
var chartsPage = function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, country, province, county, countries, provinces, counties, todayStr;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                country = params.country || "";
                province = params.province || "";
                county = params.county || "";
                countries = [];
                provinces = [];
                counties = [];
                todayStr = util_1.utc_iso(new Date());
                return [4 /*yield*/, corona_sql.getCountries(todayStr)];
            case 1:
                countries = _a.sent();
                if (!country) return [3 /*break*/, 3];
                return [4 /*yield*/, corona_sql.getProvinces(todayStr, country)];
            case 2:
                provinces = _a.sent();
                _a.label = 3;
            case 3:
                if (!province) return [3 /*break*/, 5];
                return [4 /*yield*/, corona_sql.getCounties(todayStr, country, province)];
            case 4:
                counties = _a.sent();
                _a.label = 5;
            case 5:
                res.render("charts/future", {
                    country: country,
                    province: province,
                    county: county,
                    countries: countries,
                    provinces: provinces,
                    counties: counties
                });
                return [2 /*return*/];
        }
    });
}); };
