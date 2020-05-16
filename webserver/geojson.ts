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