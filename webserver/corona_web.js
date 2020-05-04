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
var corona_sql = require("./corona_sql");
var express = require("express");
var fs = require('fs');
var url = require('url');
var state_abbr = require('./state_abbr');
var COLORS = require("./static/js/colors.js");
var Handlebars = require('hbs');
var NewsAPI = require('newsapi');
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
var app = express();
/* Static data url */
app.use(express.static('static'));
/* Use Handlebars */
app.set('view engine', 'hbs');
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
/* Main Page
 * The Main Page includes charts, data tables, and live stats */
var datatablePage = function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
    var params, country, province, county, entry_date, label, data, lastUpdate, mainDatapoint, _i, data_1, datapoint, dates, firstDay, lastDay, countries, provinces, counties, todayStr;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                params = url.parse(req.url, true).query;
                country = params['country'] || "";
                province = params['province'] || "";
                county = params['county'] || "";
                entry_date = params['date'] || utc_iso(new Date());
                label = getLabel(country, province, county);
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
app.get("/calculated", function (req, res) {
    res.render("calculated");
});
app.get("/", datatablePage);
/* Technical info about the charts */
app.get("/charts/info", function (req, res) {
    res.render("charts/info");
});
app.get("/future", function (req, res) { return __awaiter(void 0, void 0, void 0, function () {
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
                todayStr = utc_iso(new Date());
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
}); });
/* Map Page
 * The Map Page includes a map of the most recent cases, to the county level. */
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
/* Totals API
 * This provides results for a given country, province, or county */
app.get("/cases/totals", function (req, res) {
    var params = req.query;
    // get location and date
    var country = params.country || "";
    var province = params.province || "";
    var county = params.county || "";
    var entryDate = params.date || utc_iso(new Date());
    corona_sql.getDatapointChildren(entryDate, country, province, county).then(function (content) { return res.send(JSON.stringify(content)); });
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
 * Gives the most recent data, with missing dates filled in */
app.get("/cases/totals_sequence", function (req, res) {
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
app.get("/api/countries", function (req, res) {
    var params = url.parse(req.url, true).query;
    var entryDate = params.date || utc_iso(new Date());
    corona_sql.getCountries(entryDate).then(function (content) {
        res.json(content);
    });
});
/* Provinces API - gives a list of provinces for a given country and date */
app.get("/api/provinces", function (req, res) {
    var params = url.parse(req.url, true).query;
    var entryDate = params.date || utc_iso(new Date());
    var country = params.country || "";
    corona_sql.getProvinces(entryDate, country).then(function (content) { return res.json(content); });
});
/* County API - gives a list of counties for a given country, province, and date */
app.get("/api/counties", function (req, res) {
    var params = url.parse(req.url, true).query;
    var entryDate = params.date || utc_iso(new Date());
    var country = params.country || "";
    var province = params.province || "";
    corona_sql.getCounties(entryDate, country, province).then(function (content) { return res.json(content); });
});
/* Dates API - list all dates that we have on record */
app.get("/list/dates", function (req, res) {
    var params = url.parse(req.url, true).query;
    var country = params.country || "";
    var province = params.province || "";
    var county = params.county || "";
    corona_sql.getDates(country, province, county).then(function (content) { return res.json(content); });
});
/* Cases-by-date API - returns all cases (with a labelled location) for a given date. Used by the map */
app.get("/cases/date", function (req, res) {
    var params = url.parse(req.url, true).query;
    var date = params.date || utc_iso(new Date());
    corona_sql.getHeatmap(date).then(function (content) { return res.json(content); });
});
var geojson_query = "\nselect\n    datapoints.country,\n    datapoints.province,\n    datapoints.county,\n    datapoints.total,\n    datapoints.dtotal,\n    datapoints.recovered,\n    datapoints.drecovered,\n    datapoints.deaths,\n    datapoints.ddeaths,\n    locations.latitude,\n    locations.longitude\nfrom datapoints\ninner join locations\non\n    locations.country = datapoints.country and\n    locations.province = datapoints.province and\n    locations.county = datapoints.county\nwhere\n    datapoints.entry_date=? and\n    datapoints.country!=''\n";
// let geojson_cache = {};
// let geojson_max_age = 1000 * 60 * 15; // 15-minute caching
// app.get("/geojson", (req, res) => {
//     let entry_date = req.query['date'] || utc_iso(new Date());
//     let query = sqlstring.format(geojson_query + " and datapoints.province=''", entry_date);
//     if (query in geojson_cache) {
//         let {data, update_time} = geojson_cache[query];
//         if (Date.now() - update_time < geojson_max_age) {
//             res.json(data);
//             return;
//         }
//     }
//     get_sql(query).then(
//         content => {
//             let geojson_result = geojson(content);
//             geojson_cache[query] = {data: geojson_result, update_time: Date.now()};
//             res.json(geojson_result);
//         }
//     );
// });
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
                    country = req.params.country || '';
                    province = req.params.province || '';
                    if (country.toLowerCase() == 'world') {
                        country = '';
                    }
                    label = getLabel(country, province);
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
    });
}
;
function getChildLabel(country, province, county) {
    if (!country)
        return "country";
    if (!province)
        return "province";
    if (!county)
        return "county";
}
app.get("/api/mapdata", function (req, res) {
    var params = url.parse(req.url, true).query;
    var date = params.date || utc_iso(new Date());
    var country = params.country || '';
    var province = params.province || '';
    if (country == 'world')
        country = '';
    corona_sql.getDatapointChildren(date, country, province, '').then(function (results) {
        var resultsJSON = {
            subregions: {},
            overall: {}
        };
        var childLabel = getChildLabel(country, province);
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
});
/* Heatmap API - returns a list of lat/longs, and various properties. */
app.get("/api/heatmap", function (req, res) {
    var entryDate = req.query['date'] || utc_iso(new Date());
    corona_sql.getHeatmap(entryDate).then(function (heatmapData) {
        res.json(heatmapData);
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
app.listen(port, function () { return console.log("Server started at " + hostname + ":" + port + "!"); });
