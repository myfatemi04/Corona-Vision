const {sql} = require('./corona_sql');

let countries = sql.query("select distinct admin0 from datapoints where total > 100000", (err, result, fields) => {
    console.log(result);
});