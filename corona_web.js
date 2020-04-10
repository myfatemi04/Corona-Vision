const http = require('http');
const fs = require('fs');
const url = require('url');
const mustache = require('mustache');
const corona_sql = require('./corona_sql');
const sqlstring = require('sqlstring');

const hostname = '127.0.0.1';
const port = 4040;

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

    // base query
    let query = "select distinct country from live where country != ''";

    // require a province if necessary
    if ("need_province" in params && params.need_province == 1) { query += " and province != ''"; }

    // alphabetical order
    query += " order by country";

    // run the query
    corona_sql.sql.query(query, function(err, result, fields) {
        if (err) throw err;

        // used to convert to JSON
        let countries = result.map(({ country }) => country);
        res.end(JSON.stringify(countries));
    });
}

function list_provinces(req, res) {
    let params = url.parse(req.url, true).query;

    // require the country
    if (!("country" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct province from live where country = ?" , params.country);

    // require a county if necessary
    if ("need_admin2" in params && params.need_admin2 == 1) { query += " and admin2 != ''"; }
    
    // alphabetical order
    query += " order by province";

    corona_sql.sql.query(query,
    (err, result, fields) => {
        if (err) throw err;

        // used to convert to JSON
        let provinces = result.map(({ province }) => province);
        res.end(JSON.stringify(provinces));
    });
}

function list_admin2(req, res) {
    let params = url.parse(req.url, true).query;

    // require the country and province
    if (!("country" in params) || !("province" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct admin2 from live where country = ? and province = ? order by admin2", [params.country, params.province]);
    
    corona_sql.sql.query(query,
        (err, result, fields) => {
            if (err) throw err;
            
            // used to convert to JSON
            let admin2s = result.map(({ admin2 }) => admin2);
            res.end(JSON.stringify(admin2s));
        });
}

function totals(req, res) {
    let params = url.parse(req.url, true).query;

    // get location and date
    let country = get(params, "country") || "";
    let province = get(params, "province") || "";
    let admin2 = get(params, "admin2") || "";
    let entry_date = get(params, "date") || "live";

    // by default, table is "datapoints".
    let table = "datapoints";
    if (entry_date == "live") table = "live";
    let query = "select * from datapoints where country = " + sqlstring.escape(country);
    if (province != 'all') query += " and province = " + sqlstring.escape(province);
    if (admin2 != 'all') query += " and admin2 = " + sqlstring.escape(admin2);
    if (entry_date != 'live') query += " and entry_date = " + sqlstring.escape(entry_date);
    corona_sql.sql.query(query,
        (err, result, fields) => {
            if (err) throw err;
            res.end(JSON.stringify(result));
        });
}

function totals_sequence(req, res) {}

function first_days(req, res) {}

function by_date(req, res) {}

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
