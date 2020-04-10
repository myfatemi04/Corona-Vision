const http = require('http');
const fs = require('fs');
const url = require('url');
const mustache = require('mustache');
const corona_sql = require('./corona_sql');
const sqlstring = require('sqlstring');

const hostname = '0.0.0.0';
const port = process.argv[2] || 4040;

const pages = {
    "/": main_page,
    "/charts": (req, res) => { res.end(mustache.render(templates.charts, templates)) },
    "/map": (req, res) => { res.end(mustache.render(templates.map, templates)) },
    // "/cases/box" // cases within a box
    "/cases/totals": totals, // total cases for a region, filter by nation
    "/cases/totals_sequence": totals_sequence,
    "/cases/first_days": first_days,
    "/cases/date": by_date,
    "/list/countries": list_countries, // list countries for a date
    "/list/provinces": list_provinces, // list provinces for a country for a date
    "/list/admin2": list_admin2, // list admin2 for a province for a country for a date
    "/list/dates": list_dates, // list all entry dates
    "/whattodo": (req, res) => { res.end(mustache.render(templates.whattodo, templates)) },
    "/recent": (req, res) => { res.end(mustache.render(templates.recent, templates)) },
    "/history": (req, res) => { res.end(mustache.render(templates.spread_history, templates)) },
    "/contact": (req, res) => { res.end(mustache.render(templates.contact, templates)) }
};

function get(params, field) {
    if (field in params) return params[field];
    else return null;
}

function main_page(req, res) {
    res.end(mustache.render(templates.main_page, templates));
}

function list_countries(req, res) {
    let params = url.parse(req.url, true).query;
    let entry_date = get(params, "date") || "live";

    // base query
    let query = "select distinct country from datapoints where country != '' and entry_date = " + sqlstring.escape(entry_date);

    // require a province if necessary
    if ("need_province" in params && params.need_province == 1) { query += " and province != ''"; }

    // alphabetical order
    query += " order by country";

    send_cached_sql(query, res);
}

function list_provinces(req, res) {
    let params = url.parse(req.url, true).query;

    // require the country
    if (!("country" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct province from datapoints where country = ? and province != ''" , params.country);

    // require a county if necessary
    if ("need_admin2" in params && params.need_admin2 == 1) { query += " and admin2 != ''"; }
    
    // alphabetical order
    query += " order by province";

    send_cached_sql(query, res);
}

function list_admin2(req, res) {
    let params = url.parse(req.url, true).query;

    // require the country and province
    if (!("country" in params) || !("province" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct admin2 from datapoints where country = ? and province = ? and admin2 != '' order by admin2", [params.country, params.province]);
    
    send_cached_sql(query, res);
}

function list_dates(req, res) {
    let query = "select distinct entry_date from datapoints order by entry_date desc";

    send_cached_sql(query, res);
}

function totals(req, res) {
    let params = url.parse(req.url, true).query;

    // get location and date
    let country = get(params, "country") || "";
    let province = get(params, "province") || "";
    let admin2 = get(params, "admin2") || "";
    let entry_date = get(params, "date") || "live";

    let query = "select * from datapoints";
    
    // dont filter if the field = 'all'
    let where_conds = [];
    if (country != 'all') where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all') where_conds.push("province = " + sqlstring.escape(province));
    if (admin2 != 'all') where_conds.push("admin2 = " + sqlstring.escape(admin2));

    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }

    query += " and entry_date = " + sqlstring.escape(entry_date);

    send_cached_sql(query, res);
}

function totals_sequence(req, res) {
    let params = url.parse(req.url, true).query;

    // get location and date
    let country = get(params, "country") || "";
    let province = get(params, "province") || "";
    let admin2 = get(params, "admin2") || "";

    let query = "select * from datapoints";
    
    // dont filter if the field = 'all'
    let where_conds = [];
    if (country != 'all') where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all') where_conds.push("province = " + sqlstring.escape(province));
    if (admin2 != 'all') where_conds.push("admin2 = " + sqlstring.escape(admin2));

    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }

    query += "order by entry_date";

    send_cached_sql(query, res, content_func = (content) => {
        let labels = ['confirmed', 'recovered', 'deaths', 'active', 'dconfirmed', 'drecovered', 'ddeaths', 'dactive', 'entry_date'];
        let resp = {};

        for (let label of labels) {
            resp[label] = [];
        }

        for (let row of content) {
            for (let label of labels) {
                resp[label].push(row[label]);
            }
        }

        return JSON.stringify(resp);
    });
}

function first_days(req, res) {
    let query = sqlstring.format("select * from datapoints where is_first_day = true");
    send_cached_sql(query, res);
}

function by_date(req, res) {
    let entry_date = get(url.parse(req.url, true).query, "date") || "live";
    let query = sqlstring.format("select * from datapoints where entry_date = ? and is_primary = true", entry_date);
    send_cached_sql(query, res);
}

function send_cached_sql(query, res, content_func = (content) => JSON.stringify(content)) {
    // if this query is in the cache, and it was updated less than a minute ago, return the cached version
    if (sql_cache.hasOwnProperty(query) && (Date.now() - sql_cache[query].time) < sql_cache_age) {
        res.end(sql_cache[query].content);
    } else {
        corona_sql.sql.query(query,
            (err, result, fields) => {
                if (err) throw err;

                // updated the cache
                sql_cache[query] = {"content": content_func(result), "time": Date.now()};
                res.end(sql_cache[query].content);
            });
    }
}

const sql_cache = {};
const sql_cache_age = 60000;

const templates = {

};

const static_cache = {

};

const template_paths = [
    'chart_options', 'chart_panel', 'charts',
    'contact', 'main_page', 'map_panel', 'map', 'navbar',
    'recent', 'selectors', 'spread_history', 'styles', 'stats_panel', 'whattodo'
];

console.log("Loading templates");
for (let path of template_paths) {
    fs.readFile("node_templates/" + path + ".html", "utf-8", (err, data) => {
        templates[path] = data;
    });
}

const server = http.createServer(
    (req, res) => {
        let path = url.parse(req.url).pathname;
        if (pages.hasOwnProperty(path)) {
            res.statusCode = 200;
            res.setHeader("Content-Type", "text/html");
            pages[path](req, res)
        } else if (path.startsWith("/static/")) {
            path = path.replace("..",  "").substring(1);
            if (!static_cache.hasOwnProperty(path)) {
                if (fs.existsSync(path)) {
                    fs.readFile(path, "utf-8", (error, data) => {
                        static_cache[path] = data;
                        res.end(data)
                    });
                } else {
                    res.statusCode = 404;
                    res.end();
                }
            } else {
                res.end(static_cache[path]);
            }
        } else {
            res.statusCode = 404;
            res.end();
        }
    }
);

server.listen(port, hostname, () => {
    console.log(`Server running on ${hostname}:${port}!`);
});
