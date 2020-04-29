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
var __spreadArrays = (this && this.__spreadArrays) || function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};
exports.__esModule = true;
require("./interfaces");
var express = require('express');
var bodyparser = require('body-parser');
var fs = require('fs');
var url = require('url');
var state_abbr = require('./state_abbr');
var COLORS = require("./static/js/colors.js");
var Handlebars = require('hbs');
var corona_sql = require('./corona_sql');
var sqlstring = require('sqlstring');
var NewsAPI = require('newsapi');
var iso2 = require('iso-3166-1-alpha-2');
var newsapi = new NewsAPI(process.env.NEWS_API_KEY);
var datatables = require('./corona_datatable_back');
/* Register the "partials" - handlebars templates that can be included in other templates */
Handlebars.registerPartial("navbar", fs.readFileSync("views/navbar.hbs", "utf-8"));
Handlebars.registerPartial("styles", fs.readFileSync("views/styles.hbs", "utf-8"));
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
// Handlebars.registerPartial("map_panel", fs.readFileSync("views/map_panel.hbs", "utf-8"));
var app = express();
/* Static data url */
app.use(express.static('static'));
/* For POST request body */
app.use(bodyparser.urlencoded({
    extended: true
}));
/* Use Handlebars */
app.set('view engine', 'hbs');
/* Main Page
 * The Main Page includes charts, data tables, and live stats */
var last_update = null;
var get_datapoint = function (country, province, county, group, entry_date) { return __awaiter(void 0, void 0, void 0, function () {
    var query, query2, loc_where, last_update_result, label, data, location_datapoints, err_1;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 4, , 5]);
                query = "select * from datapoints where";
                query += " entry_date=" + sqlstring.escape(entry_date);
                if (group)
                    query += " and `group`=" + sqlstring.escape(group);
                if (country)
                    query += " and country=" + sqlstring.escape(country);
                if (!country || province)
                    query += " and province=" + sqlstring.escape(province);
                if (!province || county)
                    query += " and county=" + sqlstring.escape(county);
                query += " and total > 10";
                query2 = "select * from datapoints where ";
                query2 += " entry_date=" + sqlstring.escape(entry_date) + " and";
                loc_where = "";
                loc_where += " country=" + sqlstring.escape(country);
                loc_where += " and province=" + sqlstring.escape(province);
                loc_where += " and county=" + sqlstring.escape(county);
                loc_where += " and total > 10";
                query2 += loc_where;
                return [4 /*yield*/, get_sql("select MAX(update_time) as update_time from datapoints where entry_date=" + sqlstring.escape(entry_date) + ";")];
            case 1:
                last_update_result = _a.sent();
                last_update = last_update_result[0]['update_time'];
                label = county;
                if (!county)
                    label = province;
                if (!province)
                    label = country;
                if (!country)
                    label = "World";
                return [4 /*yield*/, get_sql(query)];
            case 2:
                data = _a.sent();
                return [4 /*yield*/, get_sql(query2)];
            case 3:
                location_datapoints = _a.sent();
                if (location_datapoints.length == 0) {
                    return [2 /*return*/, null];
                }
                return [2 /*return*/, {
                        location_datapoint: location_datapoints[0],
                        loc_where: loc_where,
                        label: label,
                        data: data
                    }];
            case 4:
                err_1 = _a.sent();
                console.error("Error while querying for datapoints at that location!");
                return [2 /*return*/, { "error": err_1 }];
            case 5: return [2 /*return*/];
        }
    });
}); };
var childSelector = function (country, province) {
    return (!country ?
        "country != '' and province=''" :
        !province ?
            "country = " + sqlstring.escape(country) + " and province != ''" :
            "country = " + sqlstring.escape(country) + " and province = " + sqlstring.escape(province) + " and county != ''");
};
var childAndParentSelector = function (country, province) {
    return (!country ?
        "province=''" :
        !province ?
            "country = " + sqlstring.escape(country) + " and county=''" :
            "country = " + sqlstring.escape(country) + " and province = " + sqlstring.escape(province));
};
var getChildDates = function (country, province) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                if (!country)
                    country = "";
                if (!province)
                    province = "";
                return [4 /*yield*/, get_sql("select distinct entry_date from datapoints where " +
                        childSelector(country, province) +
                        " order by entry_date desc")];
            case 1: return [2 /*return*/, _a.sent()];
        }
    });
}); };
var getLabel = function (country, province, county) {
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
};
var get_all_dates = function (loc_where) { return __awaiter(void 0, void 0, void 0, function () {
    var entry_dates_result, entry_dates, err_2;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                return [4 /*yield*/, get_sql("select distinct entry_date from datapoints where" + loc_where + " order by entry_date desc")];
            case 1:
                entry_dates_result = _a.sent();
                entry_dates = entry_dates_result.map(function (x) { return utc_iso(x['entry_date']); });
                return [2 /*return*/, {
                        first_available_day: entry_dates[entry_dates.length - 1],
                        last_available_day: entry_dates[0],
                        entry_dates: entry_dates
                    }];
            case 2:
                err_2 = _a.sent();
                console.error("Error while obtaining list of dates! Error:", err_2);
                return [2 /*return*/, { "error": err_2 }];
            case 3: return [2 /*return*/];
        }
    });
}); };
var getDatapointFromRequest = function (req) { return __awaiter(void 0, void 0, void 0, function () {
    var params, group, country, province, county, entry_date;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                group = params['region'] || "";
                country = params['country'] || "";
                province = params['province'] || "";
                county = params['county'] || "";
                entry_date = params['date'] || utc_iso(new Date());
                return [4 /*yield*/, get_datapoint(country, province, county, group, entry_date)];
            case 1: return [2 /*return*/, _a.sent()];
        }
    });
}); };
var data_table_page = function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, group, country, province, county, entry_date, datapoint_response, location_datapoint, loc_where, label, data, date_response, first_available_day, last_available_day, entry_dates, countries, provinces, counties, err_3, err_4, err_5;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                group = params['region'] || "";
                country = params['country'] || "";
                province = params['province'] || "";
                county = params['county'] || "";
                entry_date = params['date'] || utc_iso(new Date());
                return [4 /*yield*/, get_datapoint(country, province, county, group, entry_date)];
            case 1:
                datapoint_response = _a.sent();
                if (!datapoint_response) {
                    res.render("main_page", { error: "Location not found" });
                    return [2 /*return*/];
                }
                else if (datapoint_response.error) {
                    res.render("main_page", { error: datapoint_response.error });
                    return [2 /*return*/];
                }
                location_datapoint = datapoint_response.location_datapoint, loc_where = datapoint_response.loc_where, label = datapoint_response.label, data = datapoint_response.data;
                return [4 /*yield*/, get_all_dates(loc_where)];
            case 2:
                date_response = _a.sent();
                if (!date_response) {
                    res.render("main_page", { error: "Dates couldn't be loaded" });
                    return [2 /*return*/];
                }
                else if (date_response.error) {
                    res.render("main_page", { error: date_response.error });
                    return [2 /*return*/];
                }
                first_available_day = date_response.first_available_day, last_available_day = date_response.last_available_day, entry_dates = date_response.entry_dates;
                location_datapoint.last_update = datatables.format_update_time(location_datapoint.update_time);
                countries = [];
                provinces = [];
                counties = [];
                _a.label = 3;
            case 3:
                _a.trys.push([3, 5, , 6]);
                return [4 /*yield*/, getCountries(entry_date)];
            case 4:
                countries = _a.sent();
                return [3 /*break*/, 6];
            case 5:
                err_3 = _a.sent();
                console.error("Error when retrieving country list!", err_3);
                return [3 /*break*/, 6];
            case 6:
                if (!country) return [3 /*break*/, 10];
                _a.label = 7;
            case 7:
                _a.trys.push([7, 9, , 10]);
                return [4 /*yield*/, getProvinces(country, entry_date)];
            case 8:
                provinces = _a.sent();
                return [3 /*break*/, 10];
            case 9:
                err_4 = _a.sent();
                console.error("Error when retrieving province list!", err_4);
                return [3 /*break*/, 10];
            case 10:
                if (!province) return [3 /*break*/, 14];
                _a.label = 11;
            case 11:
                _a.trys.push([11, 13, , 14]);
                return [4 /*yield*/, getCounties(country, province, entry_date)];
            case 12:
                counties = _a.sent();
                return [3 /*break*/, 14];
            case 13:
                err_5 = _a.sent();
                console.error("Error when retrieving county list!", err_5);
                return [3 /*break*/, 14];
            case 14:
                res.render("main_page", __assign(__assign({}, datatables.make_rows(data, country, province, county, entry_date)), { last_update: datatables.format_update_time(last_update), country: country, province: province, county: county, label: label, location_datapoint: location_datapoint, entry_date: entry_date, entry_dates: entry_dates, isLast: (last_available_day == entry_date), isFirst: (first_available_day == entry_date), countries: countries, provinces: provinces, counties: counties, COLORS: COLORS }));
                return [2 /*return*/];
        }
    });
}); };
app.get("/calculated", function (req, res) {
    res.render("calculated");
});
app.get("/", data_table_page);
/* Technical info about the charts */
app.get("/charts/info", function (req, res) {
    res.render("charts/info");
});
function noneUndefined(row) {
    if (('country' in row) && !row.country)
        return false;
    if (('province' in row) && !row.province)
        return false;
    if (('county' in row) && !row.county)
        return false;
    return true;
}
var getCountries = function (entryDate) { return __awaiter(void 0, void 0, void 0, function () {
    var query, countriesResult, err_6;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                query = "select distinct country from datapoints where total > 10";
                if (typeof entryDate != "undefined")
                    query += " and entry_date = " + sqlstring.escape(entryDate);
                return [4 /*yield*/, get_sql(query)];
            case 1:
                countriesResult = _a.sent();
                return [2 /*return*/, countriesResult.filter(noneUndefined)];
            case 2:
                err_6 = _a.sent();
                console.error("Error when retrieving country list!", err_6);
                return [2 /*return*/, []];
            case 3: return [2 /*return*/];
        }
    });
}); };
var getProvinces = function (country, entryDate) { return __awaiter(void 0, void 0, void 0, function () {
    var query, provincesResult, err_7;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                query = sqlstring.format("select distinct province from datapoints where country = ? and total > 10", [country]);
                if (typeof entryDate != "undefined")
                    query += " and entry_date = " + sqlstring.escape(entryDate);
                return [4 /*yield*/, get_sql(query)];
            case 1:
                provincesResult = _a.sent();
                return [2 /*return*/, provincesResult.filter(noneUndefined)];
            case 2:
                err_7 = _a.sent();
                console.error("Error when retrieving province list!", err_7);
                return [2 /*return*/, []];
            case 3: return [2 /*return*/];
        }
    });
}); };
var getCounties = function (country, province, entryDate) { return __awaiter(void 0, void 0, void 0, function () {
    var query, countiesResult, err_8;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                _a.trys.push([0, 2, , 3]);
                query = sqlstring.format("select distinct county from datapoints where country = ? and province = ? and total > 10", [country, province]);
                if (typeof entryDate != "undefined")
                    query += " and entry_date = " + sqlstring.escape(entryDate);
                return [4 /*yield*/, get_sql(query)];
            case 1:
                countiesResult = _a.sent();
                return [2 /*return*/, countiesResult.filter(noneUndefined)];
            case 2:
                err_8 = _a.sent();
                console.error("Error when retrieving county list!", err_8);
                return [2 /*return*/, []];
            case 3: return [2 /*return*/];
        }
    });
}); };
app.get("/future", function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, country, province, county, countries, provinces, counties, err_9, err_10, err_11;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                country = params.country || "";
                province = params.province || "";
                county = params.county || "";
                if (typeof country == "object") {
                    country = country[0];
                }
                if (typeof province == "object") {
                    province = province[0];
                }
                if (typeof county == "object") {
                    county = county[0];
                }
                countries = [];
                provinces = [];
                counties = [];
                _a.label = 1;
            case 1:
                _a.trys.push([1, 3, , 4]);
                return [4 /*yield*/, getCountries()];
            case 2:
                countries = _a.sent();
                return [3 /*break*/, 4];
            case 3:
                err_9 = _a.sent();
                console.error("Error when retrieving country list!", err_9);
                return [3 /*break*/, 4];
            case 4:
                if (!country) return [3 /*break*/, 8];
                _a.label = 5;
            case 5:
                _a.trys.push([5, 7, , 8]);
                return [4 /*yield*/, getProvinces(country)];
            case 6:
                provinces = _a.sent();
                return [3 /*break*/, 8];
            case 7:
                err_10 = _a.sent();
                console.error("Error when retrieving province list!", err_10);
                return [3 /*break*/, 8];
            case 8:
                if (!province) return [3 /*break*/, 12];
                _a.label = 9;
            case 9:
                _a.trys.push([9, 11, , 12]);
                return [4 /*yield*/, getCounties(country, province)];
            case 10:
                counties = _a.sent();
                return [3 /*break*/, 12];
            case 11:
                err_11 = _a.sent();
                console.error("Error when retrieving county list!", err_11);
                return [3 /*break*/, 12];
            case 12:
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
}); });
// /* Map Page
//  * The Map Page includes a map of the most recent cases, to the county level. */
app.get("/maps/circle", function (req, res) {
    res.render("maps/circle");
});
/* Map Page
 * The Map Page includes a map of the most recent cases, to the county level. */
app.get("/maps/heat", function (req, res) {
    res.render("maps/heat");
});
/* Disclaimer lol
 */
app.get("/disclaimer", function (req, res) {
    res.render("details/disclaimer");
});
/* Totals Table (backend)
 * Provides an HTML table that can be inserted into the main page */
app.get("/cases/totals_table", function (req, res) {
    var params = req.query;
    // get location and date
    var country = get(params, "country") || "";
    var province = get(params, "province") || "";
    var county = get(params, "county") || "";
    var entry_date = get(params, "date") || utc_iso(new Date());
    var query = "select * from datapoints";
    // dont filter if the field = 'all'
    var where_conds = [];
    if (country != 'all')
        where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all')
        where_conds.push("province = " + sqlstring.escape(province));
    if (county != 'all')
        where_conds.push("county = " + sqlstring.escape(county));
    where_conds.push("total > 10");
    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }
    query += " and entry_date = " + sqlstring.escape(entry_date);
    get_sql(query, "table_" + query).then(function (content) {
        res.send(datatables.make_rows(content, country, province, county, entry_date).table_rows);
    });
});
/* Totals API
 * This provides results for a given country, province, or county */
app.get("/cases/totals", function (req, res) {
    var params = req.query;
    // get location and date
    var country = get(params, "country") || "";
    var province = get(params, "province") || "";
    var county = get(params, "county") || "";
    var entry_date = get(params, "date") || utc_iso(new Date());
    var query = "select * from datapoints";
    // dont filter if the field = 'all'
    var where_conds = [];
    if (country != 'all')
        where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all')
        where_conds.push("province = " + sqlstring.escape(province));
    if (county != 'all')
        where_conds.push("county = " + sqlstring.escape(county));
    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }
    query += " and entry_date = " + sqlstring.escape(entry_date);
    get_sql(query).then(function (content) { return res.send(JSON.stringify(content)); });
});
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
/* Totals Sequence API
 * Gives the most recent data, with missing dates __not__ filled in (yet) */
app.get("/cases/totals_sequence", function (req, res) {
    var params = req.query;
    // get location and date
    var country = params.country || "";
    var province = params.province || "";
    var county = params.county || "";
    var query = "select * from datapoints";
    // dont filter if the field = 'all'
    var where_conds = [];
    if (country != 'all')
        where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all')
        where_conds.push("province = " + sqlstring.escape(province));
    if (county != 'all')
        where_conds.push("county = " + sqlstring.escape(county));
    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }
    query += " order by entry_date";
    get_sql(query).then(function (content) {
        var labels = ['total', 'recovered', 'deaths'];
        var resp;
        resp.entry_date = [];
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
            resp.entry_date.push(utc_iso(day));
            for (var _a = 0, labels_2 = labels; _a < labels_2.length; _a++) {
                var label = labels_2[_a];
                resp[label].push(content[i][label]);
            }
            // we don't increment the data index if the next date isn't found
            day.setUTCDate(day.getUTCDate() + 1);
            if (i + 1 < content.length) {
                var content_iso = utc_iso(new Date(content[i + 1].entry_date));
                if (utc_iso(day) == content_iso)
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
});
/* Countries API - returns a list of all countries for a given date */
app.get("/list/countries", function (req, res) {
    var params = req.query;
    var entry_date = get(params, "date") || utc_iso(new Date());
    // base query
    var query = "select distinct country from datapoints where country != '' and entry_date = " + sqlstring.escape(entry_date);
    // require a province if necessary
    if ("need_province" in params && params.need_province == 1) {
        query += " and province != ''";
    }
    // alphabetical order
    query += " order by country";
    get_sql(query).then(function (content) {
        res.json(content);
    });
});
/* Provinces API - gives a list of provinces for a given country and date */
app.get("/list/provinces", function (req, res) {
    var params = req.query;
    // require the country
    if (!("country" in params))
        res.end();
    // base query
    var query = sqlstring.format("select distinct province from datapoints where country = ? and province != ''", params.country);
    // require a county if necessary
    if ("need_county" in params && params.need_county == 1) {
        query += " and county != ''";
    }
    // alphabetical order
    query += " order by province";
    get_sql(query).then(function (content) { return res.json(content); });
});
/* County API - gives a list of counties for a given country, province, and date */
app.get("/list/county", function (req, res) {
    var params = req.query;
    // require the country and province
    if (!("country" in params) || !("province" in params))
        res.end();
    // base query
    var query = sqlstring.format("select distinct county from datapoints where country = ? and province = ? and county != '' order by county", [params.country, params.province]);
    get_sql(query).then(function (content) { return res.json(content); });
});
/* Dates API - list all dates that we have on record */
app.get("/list/dates", function (req, res) {
    var params = url.parse(req.url, true).query;
    var query = "select distinct entry_date from datapoints";
    if (params.country)
        query += " where country = " + sqlstring.escape(params.country) + " and province != ''";
    query += " order by entry_date desc";
    get_sql(query).then(function (content) { return res.json(content); });
});
/* First Days API - returns the stats for each country on the first day of infection */
app.get("/cases/first_days", function (req, res) {
    var query = sqlstring.format("select * from datapoints where is_first_day = true order by entry_date;");
    get_sql(query).then(function (content) { return res.json(content); });
});
/* Cases-by-date API - returns all cases (with a labelled location) for a given date. Used by the map */
app.get("/cases/date", function (req, res) {
    var entry_date = get(req.query, "date") || utc_iso(new Date());
    var query = sqlstring.format("select * from datapoints where entry_date = ? and latitude != 0 and longitude != 0 and county = '' and country != ''", entry_date);
    get_sql(query).then(function (content) { return res.json(content); });
});
var geojson_query = "\nselect\n    datapoints.country,\n    datapoints.province,\n    datapoints.county,\n    datapoints.total,\n    datapoints.dtotal,\n    datapoints.recovered,\n    datapoints.drecovered,\n    datapoints.deaths,\n    datapoints.ddeaths,\n    locations.latitude,\n    locations.longitude\nfrom datapoints\ninner join locations\non\n    locations.country = datapoints.country and\n    locations.province = datapoints.province and\n    locations.county = datapoints.county\nwhere\n    datapoints.entry_date=? and\n    datapoints.country!=''\n";
var geojson_cache = {};
var geojson_max_age = 1000 * 60 * 15; // 15-minute caching
app.get("/geojson", function (req, res) {
    var entry_date = req.query['date'] || utc_iso(new Date());
    var query = sqlstring.format(geojson_query + " and datapoints.province=''", entry_date);
    if (query in geojson_cache) {
        var _a = geojson_cache[query], data = _a.data, update_time = _a.update_time;
        if (Date.now() - update_time < geojson_max_age) {
            res.json(data);
            return;
        }
    }
    get_sql(query).then(function (content) {
        var geojson_result = geojson(content);
        geojson_cache[query] = { data: geojson_result, update_time: Date.now() };
        res.json(geojson_result);
    });
});
function geojson(content) {
    var feature_list = [];
    var i = 0;
    for (var _i = 0, content_1 = content; _i < content_1.length; _i++) {
        var datapoint = content_1[_i];
        var name_1 = datapoint.country || "World";
        i += 1;
        if (datapoint.province)
            name_1 = datapoint.province + ", " + name_1;
        if (datapoint.county)
            name_1 = datapoint.county + ", " + name_1;
        feature_list.push({
            id: i,
            type: "Feature",
            properties: {
                name: name_1,
                total: datapoint.total,
                deaths: datapoint.deaths,
                recovered: datapoint.recovered,
                dtotal: datapoint.dtotal,
                ddeaths: datapoint.ddeaths,
                drecovered: datapoint.drecovered,
                latitude: datapoint.latitude,
                longitude: datapoint.longitude
            },
            geometry: {
                "type": "Point",
                "coordinates": [
                    datapoint.longitude, datapoint.latitude
                ]
            }
        });
    }
    return {
        type: "FeatureCollection",
        features: feature_list
    };
}
app.get("/api/countries", function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, date, query, results, resultsJSON, _i, results_1, result, err_12;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                date = params['date'] || utc_iso(new Date());
                query = sqlstring.format("\n        select country, total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints\n        where entry_date=?\n        and country!=''\n        and province='';\n    ", date);
                _a.label = 1;
            case 1:
                _a.trys.push([1, 3, , 4]);
                return [4 /*yield*/, get_sql(query)];
            case 2:
                results = _a.sent();
                resultsJSON = {};
                for (_i = 0, results_1 = results; _i < results_1.length; _i++) {
                    result = results_1[_i];
                    resultsJSON[iso2.getCode(result.country)] = result;
                }
                res.json(resultsJSON);
                return [3 /*break*/, 4];
            case 3:
                err_12 = _a.sent();
                console.error(err_12);
                return [3 /*break*/, 4];
            case 4: return [2 /*return*/];
        }
    });
}); });
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
    'United States': __spreadArrays(Object.keys(state_abbr))
};
app.get("/maps/", countryMap);
app.get("/maps/:country", countryMap);
app.get("/maps/:country/:province", countryMap);
function countryMap(req, res) {
    return __awaiter(this, void 0, void 0, function () {
        var country, province, label, dates;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    country = req.params.country;
                    province = req.params.province;
                    if (country.toLowerCase() == 'world') {
                        country = '';
                    }
                    label = getLabel(country, province);
                    return [4 /*yield*/, getChildDates(country, province)];
                case 1:
                    dates = _a.sent();
                    res.render("maps/country", {
                        country: country,
                        province: province,
                        entryDates: dates.map(function (date) { return utc_iso(date.entry_date); }),
                        relatedMaps: mapTree[label],
                        label: label
                    });
                    return [2 /*return*/];
            }
        });
    });
}
;
function childLabel(country, province, county) {
    if (!country)
        return "country";
    if (!province)
        return "province";
    if (!county)
        return "county";
}
app.get("/api/mapdata", function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, date, country, province, childLabel_, query, results, resultsJSON, _i, results_2, result, err_13;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                date = params.date || utc_iso(new Date());
                country = params.country || '';
                province = params.province || '';
                if (country == 'world')
                    country = '';
                childLabel_ = childLabel(country, province);
                query = sqlstring.format("\n        select " + childLabel_ + ", total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints\n        where entry_date=?\n        and " + childAndParentSelector(country, province), date);
                _a.label = 1;
            case 1:
                _a.trys.push([1, 3, , 4]);
                return [4 /*yield*/, get_sql(query)];
            case 2:
                results = _a.sent();
                resultsJSON = {
                    subregions: {},
                    overall: {}
                };
                for (_i = 0, results_2 = results; _i < results_2.length; _i++) {
                    result = results_2[_i];
                    if (result[childLabel_]) {
                        resultsJSON.subregions[result[childLabel_]] = result;
                    }
                    else {
                        resultsJSON.overall = result;
                    }
                }
                res.json(resultsJSON);
                return [3 /*break*/, 4];
            case 3:
                err_13 = _a.sent();
                console.error(err_13);
                return [3 /*break*/, 4];
            case 4: return [2 /*return*/];
        }
    });
}); });
app.get("/api/countries/csv", function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, date, query, results, overall, _i, results_3, result, err_14;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                date = params['date'] || utc_iso(new Date());
                query = sqlstring.format("\n        select country, total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints\n        where entry_date=?\n        and country!=''\n        and province='';\n    ", date);
                _a.label = 1;
            case 1:
                _a.trys.push([1, 3, , 4]);
                return [4 /*yield*/, get_sql(query)];
            case 2:
                results = _a.sent();
                overall = 'country,total';
                for (_i = 0, results_3 = results; _i < results_3.length; _i++) {
                    result = results_3[_i];
                    overall += "\n" + result.country + "," + result.total;
                }
                res.send(overall);
                return [3 /*break*/, 4];
            case 3:
                err_14 = _a.sent();
                console.error(err_14);
                return [3 /*break*/, 4];
            case 4: return [2 /*return*/];
        }
    });
}); });
/* Heatmap API - returns a list of lat/longs, and various properties. */
var heatmap_cache = {};
var heatmap_max_age = 1000 * 60 * 15;
app.get("/api/heatmap", function (req, res) {
    var entry_date = req.query['date'] || utc_iso(new Date());
    var query = sqlstring.format(geojson_query + " and\n    (\n        datapoints.county!='' or\n        (\n            datapoints.country!='United States' and\n            datapoints.country!='Portugal' and\n            datapoints.country!='Netherlands'\n        )\n    ) and\n    locations.latitude is not null", entry_date);
    if (query in heatmap_cache) {
        var _a = heatmap_cache[query], data = _a.data, update_time = _a.update_time;
        if (Date.now() - update_time < heatmap_max_age) {
            res.json(data);
            return;
        }
    }
    get_sql(query).then(function (heatmap_result) {
        heatmap_result = heatmap_result.filter(function (row) { return !(row.country == 'United States' && row.county == ''); });
        heatmap_cache[query] = { data: heatmap_result, update_time: Date.now() };
        res.json(heatmap_result);
    });
});
/* What To Do Page - gives information about how to make homemade masks, general social distancing tips,
 * and organizations that you can donate to to help healthcare workers. */
app.get("/howtohelp", function (req, res) {
    res.render("details/howtohelp");
});
function removeDuplicateArticles(articles) {
    var seen_urls = {};
    var new_articles = [];
    for (var _i = 0, articles_1 = articles; _i < articles_1.length; _i++) {
        var article = articles_1[_i];
        if (!(article.url in seen_urls)) {
            new_articles.push(article);
            seen_urls[article.url] = 1;
        }
    }
    return new_articles;
}
/* Recent Page - recent news about COVID-19 from the News API */
var recent_news = {};
app.get("/news", function (req, res) {
    var possible_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'];
    var category = req.query['category'] || "general";
    if (!possible_categories.includes(category)) {
        category = "general";
    }
    /* 1000 ms/s * 60 s/m * 60 m/h * 1 h --> 1 hour cache age */
    var newsCacheExists = category in recent_news;
    if (newsCacheExists) {
        var newsCacheShouldBeUpdated = Date.now() - recent_news[category].update_time > 1000 * 60 * 360 * 1;
        if (!newsCacheShouldBeUpdated) {
            res.render("news", { articles: recent_news[category].articles });
            return;
        }
    }
    newsapi.v2.topHeadlines({
        q: 'coronavirus',
        language: 'en',
        country: 'us',
        category: category
    }).then(function (response) {
        recent_news[category] = {
            articles: removeDuplicateArticles(response.articles),
            update_time: Date.now()
        };
        res.render("news", { articles: recent_news[category].articles.slice(0, 10) });
    })["catch"](function (response) {
        console.log("There was an error during the News API! ", response);
        res.render("news", { articles: [] });
    });
});
/* History Page - lists the first days */
app.get("/history", function (req, res) {
    res.render("spread_history");
});
/* Contact Page - lists ways you can reach us for feedback or feature requests */
app.get("/contact", function (req, res) {
    res.render("details/contact");
});
/* Simulate Curve Page - would let you input the population, healthcare system capacity,
 * and growth rate of the virus. We aren't sure if we should do it yet though. */
app.get("/simulate/curve", function (req, res) {
    res.render("simulate_curve");
});
/* Sources Page - lists the sources we use (Worldometers, BNO news, JHU, covid.iscii.es, etc.) */
app.get("/sources", function (req, res) {
    res.render("details/sources");
});
app.get("/statisticsInfo", function (req, res) {
    res.render("details/statisticsInfo");
});
app.get("/test-gcloud", function (req, res) {
    res.send("Domain is directed to Google Cloud App Engine");
});
var hostname = '0.0.0.0';
var port = process.env.PORT || 4040;
function get(params, field) {
    if (field in params)
        return params[field];
    else
        return null;
}
var sql_cache = {};
var sql_cache_age = 60000;
function get_sql(query, key) {
    if (!key)
        key = query;
    return new Promise(function (resolve, reject) {
        // if this query is in the cache, and it was updated less than a minute ago, return the cached version
        if (sql_cache.hasOwnProperty(key) && (Date.now() - sql_cache[key].time) < sql_cache_age) {
            resolve(sql_cache[key].content);
        }
        else {
            corona_sql.sql.query(query, function (err, result, fields) {
                if (err)
                    throw err;
                // updated the cache
                sql_cache[key] = { "content": result, "time": Date.now() };
                resolve(sql_cache[key].content);
            });
        }
    });
}
app.listen(port, function () { return console.log("Server started at " + hostname + ":" + port + "!"); });
