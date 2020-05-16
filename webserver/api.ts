import * as corona_sql from "./corona_sql";
import { utc_iso } from "./util";

let url = require("url");

/* Totals API
 * This provides results for a given country, province, or county */
let totalsAPI = async(req, res) => {
    let params = req.query;

    // get location and date
    let country = params.country || "";
    let province = params.province || "";
    let county = params.county || "";
    let entryDate = params.date || utc_iso(new Date());

    corona_sql.getDatapointChildren(entryDate as string, country as string, province as string, county as string).then(
        content => res.send(JSON.stringify(content))
    );
};

/* Totals Sequence API
 * Gives the most recent data, with missing dates filled in */
let totalsSequenceAPI = (req, res) => {
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
};

/* Countries API - returns a list of all countries for a given date */
let countriesAPI = (req, res) => {
    let params = url.parse(req.url, true).query;
    let entryDate = params.date as string || utc_iso(new Date());

    corona_sql.getCountries(entryDate).then(
        content => {
            res.json(content);
        }
    );
};

/* Provinces API - gives a list of provinces for a given country and date */
let provincesAPI = (req, res) => {
    let params = url.parse(req.url, true).query;
    let entryDate = params.date as string || utc_iso(new Date());
    let country = params.country as string || "";

    corona_sql.getProvinces(entryDate, country).then(
        content => res.json(content)
    );
};

/* County API - gives a list of counties for a given country, province, and date */
let countiesAPI = (req, res) => {
    let params = url.parse(req.url, true).query;
    let entryDate = params.date as string || utc_iso(new Date());
    let country = params.country as string || "";
    let province = params.province as string || "";

    corona_sql.getCounties(entryDate, country, province).then(
        content => res.json(content)
    );
};

/* Dates API - list all dates that we have on record */
let listDates = (req, res) => {
    let params = url.parse(req.url, true).query;
    let country = params.country as string || "";
    let province = params.province as string || "";
    let county = params.county as string || "";
    
    corona_sql.getDates(country, province, county).then(
        content => res.json(content)
    );
};

/* Cases-by-date API - returns all cases (with a labelled location) for a given date. Used by the map */
let dateCasesAPI = (req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params.date as string || utc_iso(new Date());
    corona_sql.getHeatmap(date).then( 
        content => res.json(content)
    );
};

export {
    totalsAPI,
    totalsSequenceAPI,
    dateCasesAPI,
    listDates,

    countriesAPI,
    provincesAPI,
    countiesAPI
};