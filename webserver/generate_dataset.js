const {sql} = require('./corona_sql');

let countries = sql.query("select distinct country from datapoints where total > 100000", (err, result, fields) => {
    console.log(result);
});