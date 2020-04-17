const mysql = require('mysql');

let con = mysql.createConnection(
    process.env.DATABASE_URL
);

con.connect(function(err) {
    if (err) throw err;
    console.log("Connected to the Google Cloud SQL server!");
});

module.exports = {
    sql: con
};

