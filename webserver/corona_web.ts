import "./interfaces"

const express = require('express');
const bodyparser = require('body-parser');
const fs = require('fs');
const url = require('url');
const state_abbr = require('./state_abbr');
const COLORS = require("./static/js/colors.js");

const Handlebars = require('hbs');
const corona_sql = require('./corona_sql');
const sqlstring = require('sqlstring');
const NewsAPI = require('newsapi');
const iso2 = require('iso-3166-1-alpha-2');

const newsapi = new NewsAPI(process.env.NEWS_API_KEY);

const datatables = require('./corona_datatable_back');

/* Register the "partials" - handlebars templates that can be included in other templates */
Handlebars.registerPartial("navbar", fs.readFileSync("views/navbar.hbs", "utf-8"));
Handlebars.registerPartial("styles", fs.readFileSync("views/styles.hbs", "utf-8"));
Handlebars.registerHelper('ifeq', function (a, b, options) {
    if (a == b) { return options.fn(this); }
    return options.inverse(this);
});
Handlebars.registerHelper('percent', function(a, b) {
    return (100 * a/b).toFixed(2) + "%";
});
Handlebars.registerHelper('pos', function(conditional, options) {
    if (conditional > 0) {
        return options.fn(this);
    } else {
        return options.inverse(this);
    }
});
// Handlebars.registerPartial("map_panel", fs.readFileSync("views/map_panel.hbs", "utf-8"));

let app = express();

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
let last_update = null;

const get_datapoint = async(country, province, county, group, entry_date) => {
    try {
        let query = "select * from datapoints where";
        query += " entry_date=" + sqlstring.escape(entry_date);
        if(group) query += " and `group`=" + sqlstring.escape(group);
        if(country) query += " and country=" + sqlstring.escape(country);
        if(!country || province) query += " and province=" + sqlstring.escape(province);
        if(!province || county) query += " and county=" + sqlstring.escape(county);
        query += " and total > 10";

        let query2 = "select * from datapoints where "
        query2 += " entry_date=" + sqlstring.escape(entry_date) + " and";
        let loc_where = "";
        loc_where += " country=" + sqlstring.escape(country);
        loc_where += " and province=" + sqlstring.escape(province);
        loc_where += " and county=" + sqlstring.escape(county);
        loc_where += " and total > 10";
        query2 += loc_where;

        let last_update_result = await get_sql("select MAX(update_time) as update_time from datapoints where entry_date=" + sqlstring.escape(entry_date) + ";");
        last_update = last_update_result[0]['update_time'];

        let label = county;
        if (!county) label = province;
        if (!province) label = country;
        if (!country) label = "World";

        let data = await get_sql(query);
        let location_datapoints = await get_sql(query2)

        if (location_datapoints.length == 0) {
            return null;
        }

        return {
            location_datapoint: location_datapoints[0],
            loc_where: loc_where,
            label: label,
            data: data
        };
    } catch (err) {
        console.error("Error while querying for datapoints at that location!");
        return {"error": err}
    }
}

const childSelector = (country, province) => 
    (!country ?
        `country != '' and province=''` :
        !province ?
            `country = ${sqlstring.escape(country)} and province != ''` :
            `country = ${sqlstring.escape(country)} and province = ${sqlstring.escape(province)} and county != ''`);

const childAndParentSelector = (country, province) => 
(!country ?
    `province=''` :
    !province ?
        `country = ${sqlstring.escape(country)} and county=''` :
        `country = ${sqlstring.escape(country)} and province = ${sqlstring.escape(province)}`);

const getChildDates = async(country, province) => {
    if (!country) country = "";
    if (!province) province = "";
    return await get_sql(
        `select distinct entry_date from datapoints where ` +
        childSelector(country, province) + 
        ` order by entry_date desc`
    );
}

const getLabel = (country?: string, province?: string, county?: string) => {
    let label = "World";
    if (!country) return label;
    label = country;
    if (!province) return label;
    label = province + ", " + label;
    if (!county) return label;
    label = county + ", " + label;
    return label;
}

const get_all_dates = async(loc_where) => {
    try {
        let entry_dates_result = await get_sql("select distinct entry_date from datapoints where" + loc_where + " order by entry_date desc");
        let entry_dates = entry_dates_result.map(x => utc_iso(x['entry_date']));
        return {
            first_available_day: entry_dates[entry_dates.length - 1],
            last_available_day: entry_dates[0],
            entry_dates: entry_dates
        }
    } catch (err) {
        console.error("Error while obtaining list of dates! Error:", err);
        return {"error": err}
    }
}

const getDatapointFromRequest = async (req) => {
    let params = url.parse(req.url, true).query;
    let group = params['region'] || "";
    let country = params['country'] || "";
    let province = params['province'] || "";
    let county = params['county'] || "";
    let entry_date = params['date'] || utc_iso(new Date());
    return await get_datapoint(country, province, county, group, entry_date);
}

const data_table_page = async (req, res) => {
    let params = url.parse(req.url, true).query;
    let group = params['region'] || "";
    let country = params['country'] || "";
    let province = params['province'] || "";
    let county = params['county'] || "";
    let entry_date = params['date'] || utc_iso(new Date());
    let datapoint_response = await get_datapoint(country, province, county, group, entry_date);

    if (!datapoint_response) {
        res.render("main_page", {error: "Location not found"});
        return;
    } else if (datapoint_response.error) {
        res.render("main_page", {error: datapoint_response.error});
        return;
    }

    let {location_datapoint, loc_where, label, data} = datapoint_response;

    let date_response = await get_all_dates(loc_where);
    if (!date_response) {
        res.render("main_page", {error: "Dates couldn't be loaded"});
        return;
    } else if (date_response.error) {
        res.render("main_page", {error: date_response.error});
        return;
    }

    let {first_available_day, last_available_day, entry_dates} = date_response;

    location_datapoint.last_update = datatables.format_update_time(location_datapoint.update_time);

    let countries = [];
    let provinces = [];
    let counties = [];

    try {
        countries = await getCountries(entry_date);
    } catch (err) {
        console.error("Error when retrieving country list!", err);
    }
    if (country) {
        try {
            provinces = await getProvinces(country, entry_date);
        } catch (err) {
            console.error("Error when retrieving province list!", err);
        }
    }
    if (province) {
        try {
            counties = await getCounties(country, province, entry_date);
        } catch (err) {
            console.error("Error when retrieving county list!", err);
        }
    }
        
    res.render("main_page", {
        ...datatables.make_rows(data, country, province, county, entry_date),
        last_update: datatables.format_update_time(last_update),
        country: country,
        province: province,
        county: county,
        label: label,
        location_datapoint: location_datapoint,
        entry_date: entry_date,
        entry_dates: entry_dates,
        isLast: (last_available_day == entry_date),
        isFirst: (first_available_day == entry_date),
        countries: countries,
        provinces: provinces,
        counties: counties,
        COLORS: COLORS
    });
}

app.get("/calculated", (req, res) => {
    res.render("calculated");
});

app.get("/", data_table_page);

/* Technical info about the charts */
app.get("/charts/info", (req, res) => {
    res.render("charts/info");
});

function noneUndefined(row) {
    if(('country' in row) && !row.country) return false;
    if(('province' in row) && !row.province) return false;
    if(('county' in row) && !row.county) return false;
    return true;
}

const getCountries = async(entryDate?: string) => {
    try {
        let query = "select distinct country from datapoints where total > 10";
        if (typeof entryDate != "undefined") query += " and entry_date = " + sqlstring.escape(entryDate);
        let countriesResult = await get_sql(query);
        return countriesResult.filter(noneUndefined);
    } catch (err) {
        console.error("Error when retrieving country list!", err);
        return [];
    }
}

const getProvinces = async(country: string, entryDate?: string) => {
    try {
        let query = sqlstring.format("select distinct province from datapoints where country = ? and total > 10", [country]);
        if (typeof entryDate != "undefined") query += " and entry_date = " + sqlstring.escape(entryDate);
        let provincesResult = await get_sql(query);
        return provincesResult.filter(noneUndefined);
    } catch (err) {
        console.error("Error when retrieving province list!", err);
        return [];
    }
}

const getCounties = async(country: string, province: string, entryDate?: string) => {
    try {
        let query = sqlstring.format("select distinct county from datapoints where country = ? and province = ? and total > 10", [country, province]);
        if (typeof entryDate != "undefined") query += " and entry_date = " + sqlstring.escape(entryDate);
        let countiesResult = await get_sql(query);
        return countiesResult.filter(noneUndefined);
    } catch (err) {
        console.error("Error when retrieving county list!", err);
        return [];
    }
}

app.get("/future", async(req, res) => {
    let params = url.parse(req.url, true).query;
    let country = params.country || "";
    let province = params.province || "";
    let county = params.county || "";
    if (typeof country == "object") { country = country[0]; }
    if (typeof province == "object") { province = province[0]; }
    if (typeof county == "object") { county = county[0]; }
    
    let countries = [];
    let provinces = [];
    let counties = [];
    try {
        countries = await getCountries();
    } catch (err) {
        console.error("Error when retrieving country list!", err);
    }
    if (country) {
        try {
            provinces = await getProvinces(country);
        } catch (err) {
            console.error("Error when retrieving province list!", err);
        }
    }
    if (province) {
        try {
            counties = await getCounties(country, province);
        } catch (err) {
            console.error("Error when retrieving county list!", err);
        }
    }

    res.render("charts/future", {
        country: country,
        province: province,
        county: county,
        countries: countries,
        provinces: provinces,
        counties: counties
    });
});

// /* Map Page
//  * The Map Page includes a map of the most recent cases, to the county level. */
app.get("/maps/circle", (req, res) => {
    res.render("maps/circle");
});

/* Map Page
 * The Map Page includes a map of the most recent cases, to the county level. */
app.get("/maps/heat", (req, res) => {
    res.render("maps/heat");
});

/* Disclaimer lol
 */
app.get("/disclaimer", (req, res) => {
    res.render("details/disclaimer");
});

/* Totals Table (backend)
 * Provides an HTML table that can be inserted into the main page */
app.get("/cases/totals_table", (req, res) => {
    let params = req.query;

    // get location and date
    let country = get(params, "country") || "";
    let province = get(params, "province") || "";
    let county = get(params, "county") || "";
    let entry_date = get(params, "date") || utc_iso(new Date());

    let query = "select * from datapoints";
    
    // dont filter if the field = 'all'
    let where_conds = [];
    if (country != 'all') where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all') where_conds.push("province = " + sqlstring.escape(province));
    if (county != 'all') where_conds.push("county = " + sqlstring.escape(county));
    where_conds.push("total > 10");

    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }

    query += " and entry_date = " + sqlstring.escape(entry_date);

    get_sql(query, "table_" + query).then(
        content => {
            res.send(datatables.make_rows(content, country, province, county, entry_date).table_rows);
        }
    );
});

/* Totals API
 * This provides results for a given country, province, or county */
app.get("/cases/totals", (req, res) => {
    let params = req.query;

    // get location and date
    let country = get(params, "country") || "";
    let province = get(params, "province") || "";
    let county = get(params, "county") || "";
    let entry_date = get(params, "date") || utc_iso(new Date());

    let query = "select * from datapoints";
    
    // dont filter if the field = 'all'
    let where_conds = [];
    if (country != 'all') where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all') where_conds.push("province = " + sqlstring.escape(province));
    if (county != 'all') where_conds.push("county = " + sqlstring.escape(county));

    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }

    query += " and entry_date = " + sqlstring.escape(entry_date);

    get_sql(query).then(
        content => res.send(JSON.stringify(content))
    );
});

function utc_iso(date) {
    if (typeof date == "undefined") {
        return utc_iso(new Date());
    }
    if (typeof date == "string") {
        return date;
    }
    let year = date.getUTCFullYear();
    let month = `${date.getUTCMonth() + 1}`;
    let day = `${date.getUTCDate()}`;
    month = month.padStart(2, "0");
    day = day.padStart(2, "0");
    return year + "-" + month + "-" + day;
}

/* Totals Sequence API
 * Gives the most recent data, with missing dates __not__ filled in (yet) */
app.get("/cases/totals_sequence", (req, res) => {
    let params = req.query;

    // get location and date
    let country = params.country || "";
    let province = params.province || "";
    let county = params.county || "";

    let query = "select * from datapoints";
    
    // dont filter if the field = 'all'
    let where_conds = [];
    if (country != 'all') where_conds.push("country = " + sqlstring.escape(country));
    if (province != 'all') where_conds.push("province = " + sqlstring.escape(province));
    if (county != 'all') where_conds.push("county = " + sqlstring.escape(county));

    if (where_conds.length > 0) {
        query += " where " + where_conds.join(" and ");
    }

    query += " order by entry_date";

    get_sql(query).then(
        (content) => {
            let labels = ['total', 'recovered', 'deaths'];
            let resp: TotalsSequence = {
                entry_date: [],
                total: [],
                recovered: [],
                deaths: []
            };
            
            for (let label of labels) {
                resp[label] = [];
            }

            if (content.length == 0) {
                res.json({...resp})
                return;
            }

            /* !!! This strongly relies on the date format !!! */
            let day = new Date(content[0].entry_date);
            let last_day = new Date(content[content.length - 1].entry_date);

            let i = 0;
            // <, NOT <=, because the most recent day's data is incomplete
            while (day < last_day) {
                resp.entry_date.push(utc_iso(day));
                for (let label of labels) {
                    resp[label].push(content[i][label]);
                }

                // we don't increment the data index if the next date isn't found
                day.setUTCDate(day.getUTCDate() + 1);
                if (i + 1 < content.length) {
                    let content_iso = utc_iso(new Date(content[i + 1].entry_date));
                    if (utc_iso(day) == content_iso) i += 1;
                }
            }
            
            for (let label of labels) {
                let daily_label = "d" + label;
                let last_val = 0;
                resp[daily_label] = [];
                for (let i = 0; i < resp[label].length; i++) {
                    let this_val = resp[label][i];
                    resp[daily_label].push(this_val - last_val)
                    last_val = this_val;
                }
            }

            res.json(resp);
        }
    );
});

/* Countries API - returns a list of all countries for a given date */
app.get("/list/countries", (req, res) => {
    let params = req.query;
    let entry_date = get(params, "date") || utc_iso(new Date());

    // base query
    let query = "select distinct country from datapoints where country != '' and entry_date = " + sqlstring.escape(entry_date);

    // require a province if necessary
    if ("need_province" in params && params.need_province == 1) { query += " and province != ''"; }

    // alphabetical order
    query += " order by country";

    get_sql(query).then(
        content => {
            res.json(content);
        }
    );
});

/* Provinces API - gives a list of provinces for a given country and date */
app.get("/list/provinces", (req, res) => {
    let params = req.query;

    // require the country
    if (!("country" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct province from datapoints where country = ? and province != ''" , params.country);

    // require a county if necessary
    if ("need_county" in params && params.need_county == 1) { query += " and county != ''"; }
    
    // alphabetical order
    query += " order by province";

    get_sql(query).then(
        content => res.json(content)
    );
});

/* County API - gives a list of counties for a given country, province, and date */
app.get("/list/county", (req, res) => {
    let params = req.query;

    // require the country and province
    if (!("country" in params) || !("province" in params)) res.end();

    // base query
    let query = sqlstring.format("select distinct county from datapoints where country = ? and province = ? and county != '' order by county", [params.country, params.province]);
    
    get_sql(query).then(
        content => res.json(content)
    );
});

/* Dates API - list all dates that we have on record */
app.get("/list/dates", (req, res) => {
    let params = url.parse(req.url, true).query;
    let query = "select distinct entry_date from datapoints";
    if (params.country)
        query += " where country = " + sqlstring.escape(params.country) + " and province != ''";
    query += " order by entry_date desc";

    get_sql(query).then(
        content => res.json(content)
    );
});

/* First Days API - returns the stats for each country on the first day of infection */
app.get("/cases/first_days", (req, res) => {
    let query = sqlstring.format("select * from datapoints where is_first_day = true order by entry_date;");
    get_sql(query).then(
        content => res.json(content)
    );
});

/* Cases-by-date API - returns all cases (with a labelled location) for a given date. Used by the map */
app.get("/cases/date", (req, res) => {
    let entry_date = get(req.query, "date") || utc_iso(new Date());
    let query = sqlstring.format("select * from datapoints where entry_date = ? and latitude != 0 and longitude != 0 and county = '' and country != ''", entry_date);
    get_sql(query).then( 
        content => res.json(content)
    );
});

const geojson_query = `
select
    datapoints.country,
    datapoints.province,
    datapoints.county,
    datapoints.total,
    datapoints.dtotal,
    datapoints.recovered,
    datapoints.drecovered,
    datapoints.deaths,
    datapoints.ddeaths,
    locations.latitude,
    locations.longitude
from datapoints
inner join locations
on
    locations.country = datapoints.country and
    locations.province = datapoints.province and
    locations.county = datapoints.county
where
    datapoints.entry_date=? and
    datapoints.country!=''
`;

let geojson_cache = {};
let geojson_max_age = 1000 * 60 * 15; // 15-minute caching
app.get("/geojson", (req, res) => {
    let entry_date = req.query['date'] || utc_iso(new Date());
    let query = sqlstring.format(geojson_query + " and datapoints.province=''", entry_date);
    if (query in geojson_cache) {
        let {data, update_time} = geojson_cache[query];
        if (Date.now() - update_time < geojson_max_age) {
            res.json(data);
            return;
        }
    }

    get_sql(query).then(
        content => {
            let geojson_result = geojson(content);
            geojson_cache[query] = {data: geojson_result, update_time: Date.now()};
            res.json(geojson_result);
        }
    );
});

function geojson(content) {
    let feature_list = [];
    let i = 0;
    for (let datapoint of content) {
        let name = datapoint.country || "World";
        i += 1;
        if (datapoint.province) name = datapoint.province + ", " + name;
        if (datapoint.county) name = datapoint.county + ", " + name;
        feature_list.push({
            id: i,
            type: "Feature",
            properties: {
                name: name,
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

app.get("/api/countries", async(req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params['date'] || utc_iso(new Date());
    let query = sqlstring.format(`
        select country, total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints
        where entry_date=?
        and country!=''
        and province='';
    `, date);
    try {
        let results = await get_sql(query);
        let resultsJSON = {};
        for (let result of results) {
            resultsJSON[iso2.getCode(result.country)] = result;
        }
        res.json(resultsJSON);
    } catch (err) {
        console.error(err);
    }
});

let mapTree = {
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
    'United States': [
        ...Object.keys(state_abbr)
    ]
}

app.get("/maps/", countryMap);
app.get("/maps/:country", countryMap);
app.get("/maps/:country/:province", countryMap);

async function countryMap(req, res) {
    let country = req.params.country;
    let province = req.params.province;
    if (country.toLowerCase() == 'world') {
        country = '';
    }
    let label = getLabel(country, province);
    let dates = await getChildDates(country, province);
    res.render("maps/country", {
        country: country,
        province: province,
        entryDates: dates.map(date => utc_iso(date.entry_date)),
        relatedMaps: mapTree[label],
        label: label
    });
};

function childLabel(country?: string, province?: string, county?: string) {
    if (!country) return "country";
    if (!province) return "province";
    if (!county) return "county";
}

app.get("/api/mapdata", async (req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params.date || utc_iso(new Date());
    let country = params.country || '';
    let province = params.province || '';
    if (country == 'world') country = '';

    let childLabel_ = childLabel(country, province);
    let query = sqlstring.format(`
        select ${childLabel_}, total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints
        where entry_date=?
        and ` + childAndParentSelector(country, province), date);
    try {
        let results = await get_sql(query);
        let resultsJSON = {
            subregions: {},
            overall: {}
        };
        for (let result of results) {
            if (result[childLabel_]) {
                resultsJSON.subregions[result[childLabel_]] = result;
            } else {
                resultsJSON.overall = result;
            }
        }
        res.json(resultsJSON);
    } catch (err) {
        console.error(err);
    }
});

app.get("/api/countries/csv", async(req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params['date'] || utc_iso(new Date());
    let query = sqlstring.format(`
        select country, total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints
        where entry_date=?
        and country!=''
        and province='';
    `, date);
    try {
        let results = await get_sql(query);
        let overall = 'country,total';//,dtotal,recovered,drecovered,deaths,ddeaths
        for (let result of results) {
            overall += `\n${result.country},${result.total}`;
        }
        res.send(overall);
    } catch (err) {
        console.error(err);
    }
});

/* Heatmap API - returns a list of lat/longs, and various properties. */
let heatmap_cache = {};
let heatmap_max_age = 1000 * 60 * 15;
app.get("/api/heatmap", (req, res) => {
    let entry_date = req.query['date'] || utc_iso(new Date());
    let query = sqlstring.format(geojson_query + ` and
    (
        datapoints.county!='' or
        (
            datapoints.country!='United States' and
            datapoints.country!='Portugal' and
            datapoints.country!='Netherlands'
        )
    ) and
    locations.latitude is not null`, entry_date);
    if (query in heatmap_cache) {
        let {data, update_time} = heatmap_cache[query];
        if (Date.now() - update_time < heatmap_max_age) {
            res.json(data);
            return;
        }
    }

    get_sql(query).then(
        heatmap_result => {
            heatmap_result = heatmap_result.filter(row => !(row.country == 'United States' && row.county == ''));
            heatmap_cache[query] = {data: heatmap_result, update_time: Date.now()};
            res.json(heatmap_result);
        }
    );
});


/* What To Do Page - gives information about how to make homemade masks, general social distancing tips,
 * and organizations that you can donate to to help healthcare workers. */
app.get("/howtohelp", (req, res) => {
    res.render("details/howtohelp");
});

function removeDuplicateArticles(articles) {
    let seen_urls = {};
    let new_articles = [];
    for (let article of articles) {
        if (!(article.url in seen_urls)) {
            new_articles.push(article);
            seen_urls[article.url] = 1;
        }
    }
    return new_articles;
}

/* Recent Page - recent news about COVID-19 from the News API */
let recent_news = {};
app.get("/news", (req, res) => {
    let possible_categories = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'];
    let category = req.query['category'] || "general";
    if (!possible_categories.includes(category)) {
        category = "general";
    }

    /* 1000 ms/s * 60 s/m * 60 m/h * 1 h --> 1 hour cache age */
    let newsCacheExists = category in recent_news;
    if (newsCacheExists) {
        let newsCacheShouldBeUpdated = Date.now() - recent_news[category].update_time > 1000 * 60 * 360 * 1;
        if (!newsCacheShouldBeUpdated) {
            res.render("news", {articles: recent_news[category].articles});
            return;
        }
    }
    
    newsapi.v2.topHeadlines({
        q: 'coronavirus',
        language: 'en',
        country: 'us',
        category: category
    }).then(
        response => {
            recent_news[category] = {
                articles: removeDuplicateArticles(response.articles),
                update_time: Date.now()
            }
            res.render("news", {articles: recent_news[category].articles.slice(0, 10)});
        }
    ).catch(
        response => {
            console.log("There was an error during the News API! ", response);
            res.render("news", {articles: []});
        }
    );
});

/* History Page - lists the first days */
app.get("/history", (req, res) => {
    res.render("spread_history");
});

/* Contact Page - lists ways you can reach us for feedback or feature requests */
app.get("/contact", (req, res) => {
    res.render("details/contact");
});

/* Simulate Curve Page - would let you input the population, healthcare system capacity,
 * and growth rate of the virus. We aren't sure if we should do it yet though. */
app.get("/simulate/curve", (req, res) => {
    res.render("simulate_curve");
});

/* Sources Page - lists the sources we use (Worldometers, BNO news, JHU, covid.iscii.es, etc.) */
app.get("/sources", (req, res) => {
    res.render("details/sources");
});

app.get("/statisticsInfo", (req, res) => {
    res.render("details/statisticsInfo");
});

app.get("/test-gcloud", (req, res) => {
    res.send("Domain is directed to Google Cloud App Engine");
});

const hostname = '0.0.0.0';
const port = process.env.PORT || 4040;

function get(params, field) {
    if (field in params) return params[field];
    else return null;
}

const sql_cache = {};
const sql_cache_age = 60000;
function get_sql(query: string, key?: string) {
    if (!key) key = query;
    return new Promise(function(resolve, reject) {
        // if this query is in the cache, and it was updated less than a minute ago, return the cached version
        if (sql_cache.hasOwnProperty(key) && (Date.now() - sql_cache[key].time) < sql_cache_age) {
            resolve(sql_cache[key].content);
        } else {
            corona_sql.sql.query(query,
                (err, result, fields) => {
                    if (err) throw err;

                    // updated the cache
                    sql_cache[key] = {"content": result, "time": Date.now()};
                    resolve(sql_cache[key].content);
                });
        }
    });
    
}

app.listen(port, () => console.log(`Server started at ${hostname}:${port}!`));