var geojson_query = "\nselect\n    datapoints.country,\n    datapoints.province,\n    datapoints.county,\n    datapoints.total,\n    datapoints.dtotal,\n    datapoints.recovered,\n    datapoints.drecovered,\n    datapoints.deaths,\n    datapoints.ddeaths,\n    locations.latitude,\n    locations.longitude\nfrom datapoints\ninner join locations\non\n    locations.country = datapoints.country and\n    locations.province = datapoints.province and\n    locations.county = datapoints.county\nwhere\n    datapoints.entry_date=? and\n    datapoints.country!=''\n";
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
    var feature_list = [];
    var i = 0;
    for (var _i = 0, content_1 = content; _i < content_1.length; _i++) {
        var datapoint = content_1[_i];
        var name_1 = datapoint.country || "World";
        i += 1;
        if (datapoint.province)
            name_1 = datapoint.province + ", " + name_1;
        if (datapoint.county)
            name_1 = datapoint.county + ", " + name_1;
        feature_list.push({
            id: i,
            type: "Feature",
            properties: {
                name: name_1,
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
