"use strict";
exports.__esModule = true;
var express = require("express");
var webapp_1 = require("./webapp");
var hostname = '0.0.0.0';
var port = process.env.PORT || 4040;
var app = express();
app.set('view engine', 'hbs'); // we are using Handlebars
webapp_1.registerPartials();
app.use(express.static('static')); // static content, such as images and CSS, is served through here
app.use("/", webapp_1.getRouter());
app.listen(port, function () { return console.log("Server started at " + hostname + ":" + port + "!"); });
