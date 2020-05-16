import "./interfaces"
import * as corona_sql from "./corona_sql";
import * as express from "express";
import * as path from "path";
import { utc_iso } from "./util";
import { getLabel } from "./labels";

const fs = require('fs');
const url = require('url');

const Handlebars = require('hbs');

const COLORS = require("./colors.js");
const datatables = require('./datatables');

function registerPartials() {
    /* Register the "partials" - handlebars templates that can be included in other templates */
    Handlebars.registerPartial("coronavisionNavbar", fs.readFileSync(path.join(__dirname, "views/navbar.hbs"), "utf-8"));
    Handlebars.registerPartial("coronavisionStyles", fs.readFileSync(path.join(__dirname, "views/styles.hbs"), "utf-8"));
    Handlebars.registerHelper('ifeq', function (a: any, b: any, options: any) {
        if (a == b) { return options.fn(this); }
        return options.inverse(this);
    });
    Handlebars.registerHelper('percent', function(a: number, b: number): string {
        return (100 * a/b).toFixed(2) + "%";
    });
    Handlebars.registerHelper('pos', function(conditional: number, options: any) {
        if (conditional > 0) {
            return options.fn(this);
        } else {
            return options.inverse(this);
        }
    });
}

import { totalsAPI, totalsSequenceAPI, dateCasesAPI, countriesAPI, provincesAPI, countiesAPI, listDates } from "./api";
import { getNews } from "./news";
import { countryMap, mapDataAPI, heatmapAPI } from "./maps";

function getRouter(): express.Router {
    let router = express.Router();
    router.get('/', mainPage);
    router.get('/calculated', (req, res) => res.render("calculated"));
    router.get('/charts/info', (req, res) => res.render("charts/info"));
    router.get('/future', chartsPage);
    
    router.get("/cases/totals", totalsAPI);
    router.get("/cases/totals_sequence", totalsSequenceAPI);
    router.get("/cases/date", dateCasesAPI);
    router.get("/list/dates", listDates);
    
    router.get("/api/countries", countriesAPI);
    router.get("/api/provinces", provincesAPI);
    router.get("/api/counties", countiesAPI);
    router.get("/api/mapdata", mapDataAPI);
    router.get("/api/heatmap", heatmapAPI);
    
    router.get('/maps/circle', (req, res) => res.render("maps/circle"));
    router.get('/maps/heat', (req, res) => res.render("maps/heat"));
    router.get("/maps/", countryMap);
    router.get("/maps/:country", countryMap);
    router.get("/maps/:country/:province", countryMap);

    router.get("/news", getNews);

    router.get("/howtohelp", (req, res) => res.render("details/howtohelp"));
    router.get("/contact", (req, res) => res.render("details/contact"));
    router.get("/sources", (req, res) => res.render("details/sources"));
    router.get("/statisticsInfo", (req, res) => res.render("details/statisticsInfo"));
    
    router.get("/simulate/curve", (req, res) => res.render("simulate_curve"));

    return router;
}

let mainPage = async(req, res) => {
    let params = url.parse(req.url, true).query;
    let country = params.country || "";
    let province = params.province || "";
    let county = params.county || "";
    let entry_date = params.date || utc_iso(new Date());
    let label = getLabel(country, province, county);
    let data = await corona_sql.getDatapointChildren(entry_date, country, province, county);

    if (!data) {
        res.render("error", {error: "Location not found"});
        return;
    }

    let lastUpdate = new Date(Math.max(...data.map(x => x.update_time.getTime())));
    let mainDatapoint: Datapoint;

    for (let datapoint of data) {
        if (datapoint.country == country && datapoint.province == province && datapoint.county == county) {
            mainDatapoint = datapoint;
            break;
        }
    }

    let dates = await corona_sql.getDates(country, province, county);

    let firstDay = dates[dates.length - 1];
    let lastDay = dates[0];

    let countries = [];
    let provinces = [];
    let counties = [];

    let todayStr = entry_date;
    countries = await corona_sql.getCountries(todayStr);
    if (country) provinces = await corona_sql.getProvinces(todayStr, country);
    if (province) counties = await corona_sql.getCounties(todayStr, country, province);

    res.render("main_page", {
        ...datatables.make_rows(data, country, province, county, entry_date),
        last_update: datatables.format_update_time(lastUpdate),
        mainDatapoint: mainDatapoint,
        country: country,
        province: province,
        county: county,
        entry_date: entry_date,
        label: label,
        dates: dates,
        isLast: (lastDay == entry_date),
        isFirst: (firstDay == entry_date),
        countries: countries,
        provinces: provinces,
        counties: counties,
        COLORS: COLORS
    });
};

let chartsPage = async(req, res) => {
    let params = url.parse(req.url, true).query;
    let country = params.country as string || "";
    let province = params.province as string || "";
    let county = params.county as string || "";
    
    let countries = [];
    let provinces = [];
    let counties = [];
    let todayStr = utc_iso(new Date());

    countries = await corona_sql.getCountries(todayStr);
    if (country) provinces = await corona_sql.getProvinces(todayStr, country);
    if (province) counties = await corona_sql.getCounties(todayStr, country, province);

    res.render("charts/future", {
        country: country,
        province: province,
        county: county,
        countries: countries,
        provinces: provinces,
        counties: counties
    });
};

export {
    getRouter,
    registerPartials
};