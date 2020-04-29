import * as mysql from "mysql";
import * as sqlstring from "sqlstring";
import { resolve } from "dns";

let con = mysql.createConnection(
    process.env.DATABASE_URL + "?timezone=utc"
);

con.connect(function(err) {
    if (err) throw err;
    console.log("Connected to the Google Cloud SQL server!");
});

let datapointCache = {};
let datapointChildrenCache = {};
let heatmapDataCache = {};
let dateCache = {};
let sequencesCache = {};
let countriesCache = {};
let provincesCache = {};
let countiesCache = {};

const DAILY_CHANGE_QUERY = `
select
    today.entry_date,
    today.update_time,
    today.country,
    today.province,
    today.county,
    today.total,
    yesterday.total as yesterday_total,
    today.recovered,
    yesterday.recovered as yesterday_recovered,
    today.deaths,
    yesterday.deaths as yesterday_deaths,
    today.serious,
    yesterday.serious as yesterday_serious,
    today.tests,
    yesterday.tests as yesterday_tests,
    today.source_total,
    today.source_recovered,
    today.source_deaths,
    today.source_serious,
    today.source_tests
from datapoints today
left join datapoints yesterday on 
    date(yesterday.entry_date) = date(today.entry_date - interval 1 day) and
    yesterday.country=today.country and
    yesterday.province=today.province and
    yesterday.county=today.county
`;

function where(country: string = '', province: string = '', county: string = '', type: 'children' | 'exact' | 'childRequired' = 'exact') {
    if (type == 'exact') {
        return sqlstring.format(`
            where
                today.country = ? and
                today.province = ? and
                today.county = ?
            `,
            [country, province, county]
        );
    } else {
        if (country == '') {
            return `
                where today.province = ''
            ` + (type == 'childRequired' ? ' and today.country != \'\'' : '')
        } else if (province == '') {
            return sqlstring.format(`
                where
                    today.country = ? and
                    today.county = ''
            ` + (type == 'childRequired' ? ' and today.province != \'\'' : ''), [country])
        } else if (county == '') {
            return sqlstring.format(`
                where
                    today.country = ? and
                    today.province = ?
            ` + (type == 'childRequired' ? ' and today.county != \'\'' : ''), [country, province]);
        } else {
            return sqlstring.format(`
                where
                    today.country = ? and
                    today.province = ? and
                    today.county = ?
            `, [country, province, county]);
        }
    }
}

function makeKey(entryDate: string, country: string = '', province: string = '', county: string = '', returnLocation: boolean = false): string {
    return entryDate + "_" + country + "_" + province + "_" + county + "_";
}

function getDatapointChildren(entryDate: string, country: string = '', province: string = '', county: string = ''): Promise<Datapoint[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey(entryDate, country, province, county);
        if (key in datapointChildrenCache) {
            let {cacheUpdate, content} = datapointChildrenCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = DAILY_CHANGE_QUERY + where(country, province, county, "children") + sqlstring.format(" and today.entry_date = ?", [entryDate]);


        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            datapointCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getDatapoint(entryDate: string, country: string = '', province: string = '', county: string = ''): Promise<Datapoint> {
    return new Promise((resolve, reject) => {
        let key = makeKey(entryDate, country, province, county);
        if (key in datapointCache) {
            let {cacheUpdate, content} = datapointCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }
        
        let query = DAILY_CHANGE_QUERY + where(country, province, county) + sqlstring.format(" and today.entry_date = ?", [entryDate]);
        
        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            datapointCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getHeatmap(entryDate: string): Promise<Datapoint[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey(entryDate);
        if (key in heatmapDataCache) {
            let {cacheUpdate, content} = heatmapDataCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = `
            SELECT
                data.country,
                data.province,
                data.county,
                data.total,
                data.deaths,
                data.recovered,
                loc.latitude,
                loc.longitude
            FROM datapoints data
            INNER JOIN locations loc
            ON
                loc.country=data.country AND
                loc.province=data.province AND
                loc.county=data.county
            WHERE
                data.entry_date = ?
        `;

        let formatted = sqlstring.format(query, [entryDate]);

        con.query(formatted, (err, result, fields) => {
            if (err) reject(err);

            heatmapDataCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getDates(country: string = '', province: string = '', county: string = '', type: 'children' | 'exact' | 'childRequired' = 'exact'): Promise<string[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey("", country, province, county);
        if (key in dateCache) {
            let {cacheUpdate, content} = dateCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = `
            SELECT DISTINCT
                entry_date
            FROM datapoints today
            ${where(country, province, county, type)}
            ORDER BY entry_date
        `;

        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            result = result.map(row => row.entry_date);
            dateCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getCountries(entryDate: string): Promise<string[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey(entryDate);
        if (key in countriesCache) {
            let {cacheUpdate, content} = countriesCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = `
            SELECT DISTINCT country
            FROM datapoints
            WHERE entry_date = ${sqlstring.escape(entryDate)}
            ORDER BY country
        `;

        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            result = result.map(row => row.country);
            countriesCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getProvinces(entryDate: string, country: string): Promise<string[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey(entryDate);
        if (key in provincesCache) {
            let {cacheUpdate, content} = provincesCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = `
            SELECT DISTINCT province
            FROM datapoints
            WHERE
                entry_date = ${sqlstring.escape(entryDate)} and
                country = ${sqlstring.escape(country)}
            ORDER BY province
        `;

        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            result = result.map(row => row.province);
            provincesCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getCounties(entryDate: string, country: string, province: string): Promise<string[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey(entryDate);
        if (key in countiesCache) {
            let {cacheUpdate, content} = countiesCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = `
            SELECT DISTINCT county
            FROM datapoints
            WHERE
                entry_date = ${sqlstring.escape(entryDate)} and
                country = ${sqlstring.escape(country)} and
                province = ${sqlstring.escape(province)}
            ORDER BY county
        `;

        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            result = result.map(row => row.county);
            countiesCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

function getDatapointSequence(country: string = '', province: string = '', county: string = ''): Promise<Datapoint[]> {
    return new Promise((resolve, reject) => {
        let key = makeKey("", country, province, county);
        if (key in sequencesCache) {
            let {cacheUpdate, content} = sequencesCache[key];
            if (Date.now() - cacheUpdate < 60000) {
                resolve(content);
            }
        }

        let query = `
            SELECT
                *
            FROM datapoints today
            ${where(country, province, county)}
            ORDER BY today.entry_date
        `;

        con.query(query, (err, result, fields) => {
            if (err) reject(err);

            if (!result) {
                result = [];
            }
            sequencesCache[key] = {cacheUpdate: Date.now(), content: result};
            resolve(result);
        });
    });
}

export {
    con,
    getDates,
    getDatapoint,
    getDatapointChildren,
    getDatapointSequence,
    getHeatmap,
    getCountries,
    getProvinces,
    getCounties,
};