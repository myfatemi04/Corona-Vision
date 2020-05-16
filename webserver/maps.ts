import { utc_iso } from "./util";
import { getLabel, getChildLabel } from "./labels";
import * as corona_sql from "./corona_sql";
import * as url from "url";

let stateNames = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming"
];

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
    'United States': stateNames
};

let countryMap = async(req, res) => {
    let country = req.params.country as string || '';
    let province = req.params.province as string || '';
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

let mapDataAPI = (req, res) => {
    let params = url.parse(req.url, true).query;
    let date = params.date as string || utc_iso(new Date());
    let country = params.country as string || '';
    let province = params.province as string || '';
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
};

/* Heatmap API - returns a list of lat/longs, and various properties. */
let heatmapAPI = (req, res) => {
    let entryDate = req.query['date'] || utc_iso(new Date());
    corona_sql.getHeatmap(entryDate).then(
        heatmapData => {
            res.json(heatmapData);
        }
    );
};

export {
    countryMap,
    mapDataAPI,
    heatmapAPI
}