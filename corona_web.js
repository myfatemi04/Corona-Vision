const express = require('express');
const bodyparser = require('body-parser');
const fs = require('fs');

const Handlebars = require('hbs');
const corona_sql = require('./corona_sql');
const sqlstring = require('sqlstring');

Handlebars.registerPartial("navbar", fs.readFileSync("views/navbar.hbs", "utf-8"));
Handlebars.registerPartial("styles", fs.readFileSync("views/styles.hbs", "utf-8"));
Handlebars.registerPartial("selectors", fs.readFileSync("views/selectors.hbs", "utf-8"));
Handlebars.registerPartial("chart_options", fs.readFileSync("views/chart_options.hbs", "utf-8"));
Handlebars.registerPartial("map_panel", fs.readFileSync("views/map_panel.hbs", "utf-8"));

app = express();

app.use(express.static('static'));
app.use(bodyparser.urlencoded({
    extended: true
}));

app.set('view engine', 'hbs');

app.get("/", (req, res) => {
    res.render("main_page");
});

app.get("/charts", (req, res) => {
    res.render("charts");
});

app.get("/map", (req, res) => {
    res.render("map");
});

app.get("/cases/totals", (req, res) => {
    let params = req.query;

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
});

app.get("/cases/totals_sequence", (req, res) => {
    let params = req.query;

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
});

app.get("/list/countries", (req, res) => {
    let params = req.query;
    let entry_date = get(params, "date") || "live";

    // base query
    let query = "select distinct country from datapoints where country != '' and entry_date = " + sqlstring.escape(entry_date);

    // require a province if necessary
    if ("need_province" in params && params.need_province == 1) { query += " and province != ''"; }

    // alphabetical order
    query += " order by country";

    send_cached_sql(query, res);
});

app.get("/list/provinces", (req, res) => {
    let params = req.query;

    // require the country
    if (!("country" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct province from datapoints where country = ? and province != ''" , params.country);

    // require a county if necessary
    if ("need_admin2" in params && params.need_admin2 == 1) { query += " and admin2 != ''"; }
    
    // alphabetical order
    query += " order by province";

    send_cached_sql(query, res);
});

app.get("/list/admin2", (req, res) => {
    let params = req.query;

    // require the country and province
    if (!("country" in params) || !("province" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct admin2 from datapoints where country = ? and province = ? and admin2 != '' order by admin2", [params.country, params.province]);
    
    send_cached_sql(query, res);
});

app.get("/list/dates", (req, res) => {
    let query = "select distinct entry_date from datapoints order by entry_date desc";

    send_cached_sql(query, res);
});

app.get("/cases/first_days", (req, res) => {
    let query = sqlstring.format("select * from datapoints where is_first_day = true");
    send_cached_sql(query, res);
});

app.get("/cases/date", (req, res) => {
    let entry_date = get(req.query, "date") || "live";
    let query = sqlstring.format("select * from datapoints where entry_date = ? and is_primary = true", entry_date);
    send_cached_sql(query, res);
});

app.get("/whattodo", (req, res) => {
    res.render("whattodo");
});

app.get("/recent", (req, res) => {
    res.render("recent");
});

app.get("/history", (req, res) => {
    res.render("spread_history");
});

app.get("/contact", (req, res) => {
    res.render("contact");
});

const hostname = '0.0.0.0';
const port = process.argv[2] || 4040;

function get(params, field) {
    if (field in params) return params[field];
    else return null;
}

function send_cached_sql(query, res, content_func = (content) => JSON.stringify(content)) {
    // if this query is in the cache, and it was updated less than a minute ago, return the cached version
    if (sql_cache.hasOwnProperty(query) && (Date.now() - sql_cache[query].time) < sql_cache_age) {
        res.send(sql_cache[query].content);
    } else {
        corona_sql.sql.query(query,
            (err, result, fields) => {
                if (err) throw err;

                // updated the cache
                sql_cache[query] = {"content": content_func(result), "time": Date.now()};
                res.send(sql_cache[query].content);
            });
    }
}

const sql_cache = {};
const sql_cache_age = 60000;

app.listen(port, () => console.log(`Server started at ${hostname}:${port}!`));