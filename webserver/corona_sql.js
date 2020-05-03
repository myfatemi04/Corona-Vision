"use strict";
exports.__esModule = true;
var mysql = require("mysql");
var sqlstring = require("sqlstring");
var con = mysql.createConnection(process.env.DATABASE_URL + "?timezone=utc");
exports.con = con;
con.connect(function (err) {
    if (err)
        throw err;
    console.log("Connected to the Google Cloud SQL server!");
});
var datapointCache = {};
var datapointChildrenCache = {};
var heatmapDataCache = {};
var dateCache = {};
var sequencesCache = {};
var countriesCache = {};
var provincesCache = {};
var countiesCache = {};
var DAILY_CHANGE_QUERY = "\nselect\n    today.entry_date,\n    today.update_time,\n    today.country,\n    today.province,\n    today.county,\n    today.total,\n    yesterday.total as yesterday_total,\n    today.total - yesterday.total as dtotal,\n    today.recovered,\n    yesterday.recovered as yesterday_recovered,\n    today.recovered - yesterday.recovered as drecovered,\n    today.deaths,\n    yesterday.deaths as yesterday_deaths,\n    today.deaths - yesterday.deaths as ddeaths,\n    today.serious,\n    yesterday.serious as yesterday_serious,\n    today.serious - yesterday.serious as dserious,\n    today.tests,\n    yesterday.tests as yesterday_tests,\n    today.tests - yesterday.tests as dtests\nfrom datapoints today\nleft join datapoints yesterday on \n    date(yesterday.entry_date) = date(today.entry_date - interval 1 day) and\n    yesterday.country=today.country and\n    yesterday.province=today.province and\n    yesterday.county=today.county\n";
function where(country, province, county, type) {
    if (country === void 0) { country = ''; }
    if (province === void 0) { province = ''; }
    if (county === void 0) { county = ''; }
    if (type === void 0) { type = 'exact'; }
    if (type == 'exact') {
        return sqlstring.format("\n            where\n                today.country = ? and\n                today.province = ? and\n                today.county = ?\n            ", [country, province, county]);
    }
    else {
        if (country == '') {
            return "\n                where today.province = ''\n            " + (type == 'childRequired' ? ' and today.country != \'\'' : '');
        }
        else if (province == '') {
            return sqlstring.format("\n                where\n                    today.country = ? and\n                    today.county = ''\n            " + (type == 'childRequired' ? ' and today.province != \'\'' : ''), [country]);
        }
        else if (county == '') {
            return sqlstring.format("\n                where\n                    today.country = ? and\n                    today.province = ?\n            " + (type == 'childRequired' ? ' and today.county != \'\'' : ''), [country, province]);
        }
        else {
            return sqlstring.format("\n                where\n                    today.country = ? and\n                    today.province = ? and\n                    today.county = ?\n            ", [country, province, county]);
        }
    }
}
function makeKey(entryDate, country, province, county, returnLocation) {
    if (country === void 0) { country = ''; }
    if (province === void 0) { province = ''; }
    if (county === void 0) { county = ''; }
    if (returnLocation === void 0) { returnLocation = false; }
    return entryDate + "_" + country + "_" + province + "_" + county + "_";
}
function getDatapointChildren(entryDate, country, province, county) {
    if (country === void 0) { country = ''; }
    if (province === void 0) { province = ''; }
    if (county === void 0) { county = ''; }
    return new Promise(function (resolve, reject) {
        var key = makeKey(entryDate, country, province, county);
        if (key in datapointChildrenCache) {
            var _a = datapointChildrenCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = DAILY_CHANGE_QUERY + where(country, province, county, "children") + sqlstring.format(" and today.entry_date = ?", [entryDate]);
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            datapointCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getDatapointChildren = getDatapointChildren;
function getDatapoint(entryDate, country, province, county) {
    if (country === void 0) { country = ''; }
    if (province === void 0) { province = ''; }
    if (county === void 0) { county = ''; }
    return new Promise(function (resolve, reject) {
        var key = makeKey(entryDate, country, province, county);
        if (key in datapointCache) {
            var _a = datapointCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = DAILY_CHANGE_QUERY + where(country, province, county) + sqlstring.format(" and today.entry_date = ?", [entryDate]);
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            datapointCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getDatapoint = getDatapoint;
function getHeatmap(entryDate) {
    return new Promise(function (resolve, reject) {
        var key = makeKey(entryDate);
        if (key in heatmapDataCache) {
            var _a = heatmapDataCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = "\n            SELECT\n                today.country,\n                today.province,\n                today.county,\n                today.total,\n                today.deaths,\n                today.recovered,\n                today.total - yesterday.total as dtotal,\n                loc.latitude,\n                loc.longitude\n            FROM datapoints today\n            INNER JOIN locations loc\n            ON\n                loc.country=today.country AND\n                loc.province=today.province AND\n                loc.county=today.county\n            LEFT JOIN datapoints yesterday\n            ON\n                yesterday.country=today.country AND\n                yesterday.province=today.province AND\n                yesterday.county=today.county AND\n                date(yesterday.entry_date)=date(today.entry_date - interval 1 day)\n            WHERE\n                today.entry_date = ? and\n                loc.latitude is not null\n        ";
        var formatted = sqlstring.format(query, [entryDate]);
        con.query(formatted, function (err, result, fields) {
            if (err)
                reject(err);
            heatmapDataCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getHeatmap = getHeatmap;
function getDates(country, province, county, type) {
    if (country === void 0) { country = ''; }
    if (province === void 0) { province = ''; }
    if (county === void 0) { county = ''; }
    if (type === void 0) { type = 'exact'; }
    return new Promise(function (resolve, reject) {
        var key = makeKey("", country, province, county);
        if (key in dateCache) {
            var _a = dateCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = "\n            SELECT DISTINCT\n                entry_date\n            FROM datapoints today\n            " + where(country, province, county, type) + "\n            ORDER BY entry_date desc\n        ";
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            result = result.map(function (row) { return row.entry_date; });
            dateCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getDates = getDates;
function getCountries(entryDate) {
    return new Promise(function (resolve, reject) {
        var key = makeKey(entryDate);
        if (key in countriesCache) {
            var _a = countriesCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = "\n            SELECT DISTINCT country\n            FROM datapoints\n            WHERE entry_date = " + sqlstring.escape(entryDate) + "\n            ORDER BY country\n        ";
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            result = result.map(function (row) { return row.country; });
            countriesCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getCountries = getCountries;
function getProvinces(entryDate, country) {
    return new Promise(function (resolve, reject) {
        var key = makeKey(entryDate);
        if (key in provincesCache) {
            var _a = provincesCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = "\n            SELECT DISTINCT province\n            FROM datapoints\n            WHERE\n                entry_date = " + sqlstring.escape(entryDate) + " and\n                country = " + sqlstring.escape(country) + "\n            ORDER BY province\n        ";
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            result = result.map(function (row) { return row.province; });
            provincesCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getProvinces = getProvinces;
function getCounties(entryDate, country, province) {
    return new Promise(function (resolve, reject) {
        var key = makeKey(entryDate);
        if (key in countiesCache) {
            var _a = countiesCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = "\n            SELECT DISTINCT county\n            FROM datapoints\n            WHERE\n                entry_date = " + sqlstring.escape(entryDate) + " and\n                country = " + sqlstring.escape(country) + " and\n                province = " + sqlstring.escape(province) + "\n            ORDER BY county\n        ";
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            result = result.map(function (row) { return row.county; });
            countiesCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getCounties = getCounties;
function getDatapointSequence(country, province, county) {
    if (country === void 0) { country = ''; }
    if (province === void 0) { province = ''; }
    if (county === void 0) { county = ''; }
    return new Promise(function (resolve, reject) {
        var key = makeKey("", country, province, county);
        if (key in sequencesCache) {
            var _a = sequencesCache[key], cacheUpdate = _a.cacheUpdate, content = _a.content;
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        var query = "\n            " + DAILY_CHANGE_QUERY + "\n            " + where(country, province, county) + "\n            ORDER BY today.entry_date\n        ";
        con.query(query, function (err, result, fields) {
            if (err)
                reject(err);
            if (!result) {
                result = [];
            }
            sequencesCache[key] = { cacheUpdate: Date.now(), content: result };
            resolve(result);
        });
    });
}
exports.getDatapointSequence = getDatapointSequence;
