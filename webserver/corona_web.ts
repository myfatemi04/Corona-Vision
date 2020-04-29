import "./interfaces"
import * as corona_sql from "./corona_sql";
import * as express from "express";

const bodyparser = require('body-parser');
const fs = require('fs');
const url = require('url');
const state_abbr = require('./state_abbr');
const COLORS = require("./static/js/colors.js");

const Handlebars = require('hbs');
const sqlstring = require('sqlstring');
const NewsAPI = require('newsapi');
const iso2 = require('iso-3166-1-alpha-2');

const newsapi = new NewsAPI(process.env.NEWS_API_KEY);

const datatables = require('./corona_datatable_back');

/* Register the "partials" - handlebars templates that can be included in other templates */
Handlebars.registerPartial("navbar", fs.readFileSync("views/navbar.hbs", "utf-8"));
Handlebars.registerPartial("styles", fs.readFileSync("views/styles.hbs", "utf-8"));
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

let app = express();

/* Static data url */
app.use(express.static('static'));

/* For POST request body */
app.use(bodyparser.urlencoded({
    extended: true
}));

/* Use Handlebars */
app.set('view engine', 'hbs');

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

/* Main Page
 * The Main Page includes charts, data tables, and live stats */
const datatablePage = async (req, res) => {
    let params = url.parse(req.url, true).query;
    let country = params['country'] || "";
    let province = params['province'] || "";
    let county = params['county'] || "";
    let entry_date = params['date'] || utc_iso(new Date());
    let label = getLabel(country, province, county);
    let data = await corona_sql.getDatapointChildren(entry_date, country, province, county);

    if (!data) {
        res.render("main_page", {error: "Location not found"});
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

    let firstDay = dates[0];
    let lastDay = dates[dates.length - 1];

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
}

app.get("/calculated", (req, res) => {
    res.render("calculated");
});

app.get("/", datatablePage);

/* Technical info about the charts */
app.get("/charts/info", (req, res) => {
    res.render("charts/info");
});

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

/* Totals API
 * This provides results for a given country, province, or county */
app.get("/cases/totals", (req, res) => {
    let params = req.query;

    // get location and date
    let country = params.country || "";
    let province = params.province || "";
    let county = params.county || "";
    let entryDate = params.date || utc_iso(new Date());

    corona_sql.getDatapointChildren(entryDate as string, country as string, province as string, county as string).then(
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

    corona_sql.getDatapointSequence(country as string, province as string, county as string).then(
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
app.get("/api/countries", (req, res) => {
    let params = url.parse(req.url, true).query;
    let entryDate = params.date as string || utc_iso(new Date());

    corona_sql.getCountries(entryDate).then(
        content => {
            res.json(content);
        }
    );
});

/* Provinces API - gives a list of provinces for a given country and date */
app.get("/api/provinces", (req, res) => {
    let params = url.parse(req.url, true).query;
    let entryDate = params.date as string || utc_iso(new Date());
    let country = params.country as string || "";

    corona_sql.getProvinces(entryDate, country).then(
        content => res.json(content)
    );
});

/* County API - gives a list of counties for a given country, province, and date */
app.get("/api/counties", (req, res) => {
    let params = url.parse(req.url, true).query;
    let entryDate = params.date as string || utc_iso(new Date());
    let country = params.country as string || "";
    let province = params.province as string || "";

    corona_sql.getCounties(entryDate, country, province).then(
        content => res.json(content)
    );
});

/* Dates API - list all dates that we have on record */
app.get("/list/dates", (req, res) => {
    let params = url.parse(req.url, true).query;
    let country = params.country as string || "";
    let province = params.province as string || "";
    let county = params.county as string || "";
    
    corona_sql.getDates(country, province, county).then(
        content => res.json(content)
    );
});

/* Cases-by-date API - returns all cases (with a labelled location) for a given date. Used by the map */
app.get("/cases/date", (req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params.date as string || utc_iso(new Date());
    corona_sql.getHeatmap(date).then( 
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
    let dates = await corona_sql.getDates(country, province, "", "childRequired");
    res.render("maps/country", {
        country: country,
        province: province,
        entryDates: dates,
        relatedMaps: mapTree[label],
        label: label
    });
};

function getChildLabel(country?: string, province?: string, county?: string) {
    if (!country) return "country";
    if (!province) return "province";
    if (!county) return "county";
}

app.get("/api/mapdata", (req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params.date || utc_iso(new Date());
    let country = params.country || '';
    let province = params.province || '';
    if (country == 'world') country = '';

    corona_sql.getDatapointChildren(date, country, province, '').then(
        results => {
            let resultsJSON = {
                subregions: {},
                overall: {}
            };
            let childLabel = getChildLabel(country, province);
            for (let result of results) {
                if (result[childLabel]) {
                    resultsJSON.subregions[result[childLabel]] = result;
                } else {
                    resultsJSON.overall = result;
                }
            }
            res.json(resultsJSON);
        }
    );
});

// app.get("/api/countries/csv", async(req, res) => {
//     let params = url.parse(req.url, true).query;
//     let date = params['date'] || utc_iso(new Date());
//     let query = sqlstring.format(`
//         select country, total, dtotal, recovered, drecovered, deaths, ddeaths from datapoints
//         where entry_date=?
//         and country!=''
//         and province='';
//     `, date);
//     try {
//         let results = await get_sql(query);
//         let overall = 'country,total';//,dtotal,recovered,drecovered,deaths,ddeaths
//         for (let result of results) {
//             overall += `\n${result.country},${result.total}`;
//         }
//         res.send(overall);
//     } catch (err) {
//         console.error(err);
//     }
// });

/* Heatmap API - returns a list of lat/longs, and various properties. */
app.get("/api/heatmap", (req, res) => {
    let entryDate = req.query['date'] || utc_iso(new Date());
    corona_sql.getHeatmap(entryDate).then(
        heatmapData => {
            res.json(heatmapData);
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
    let category = req.query['category'] as string || "general";
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

app.listen(port, () => console.log(`Server started at ${hostname}:${port}!`));