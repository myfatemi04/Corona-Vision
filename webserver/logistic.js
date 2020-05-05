"use strict";
exports.__esModule = true;
var ml_levenberg_marquardt_1 = require("ml-levenberg-marquardt");
/*
Logistic growth curve function.
Parameters:
    MAX: maximum value of the function (the numerator).
    T_INF: the time of the inflection point - when does the curve start to change direction?
    T_RISE: the time for the curve to reach the inflection point
    LIN: this parameter was added to model social distancing:
        the time to reach the inflection point will increase over time,
        as the disease is spreading more slowly.
*/
function logisticFunction(_a) {
    var MAX = _a[0], T_INF = _a[1], T_RISE = _a[2], LIN = _a[3];
    return function (t) { return MAX / (1 + Math.exp(-(t - T_INF) / (T_RISE + LIN * t))); };
}
/**
 * Converts a list of dates into a list of numbers, representing the number
 * of days since Day 1.
 * Assumes the dates are *sorted*.
 * @author Michael Fatemi
 * @param entryDates The list of dates to convert into indexed numbers.
 * @returns A list of numbers, 0-indexed based on the start date.
 */
function datesToNumbers(entryDates) {
    var minDate = entryDates[0];
    var dateLength = 86400 * 1000;
    return entryDates.map(function (x) { return (x.getTime() - minDate.getTime()) / dateLength; });
}
/**
 * Logistic regression!
 * @param x The x values (dates)
 * @param y The y values (total cases, total deaths, etc.)
 * @returns The parameters for a logistic regression that fit these stats.
 * @author Michael Fatemi, Fredrik Fatemi
 */
function fit(x, y) {
    var data = {
        x: x,
        y: y
    };
    // Order: MAX, T_INF, T_RISE, LIN
    var minValues = [
        y[y.length - 1],
        0,
        1,
        0 // lin: must be at least 0 (social distancing shouldn't decrease)
    ];
    var maxValues = [
        7.3e9,
        800,
        800,
        20
    ];
    var startingValues = [
        y[y.length - 1],
        x[Math.floor(x.length / 2)],
        40,
        1 // lin: starts at a slope of one day per day
    ];
    var options = {
        initialValues: startingValues,
        minValues: minValues,
        maxValues: maxValues,
        gradientDifference: 10e-2,
        maxIterations: 1000,
        errorTolerance: 10e-3
    };
    var fittedParams = ml_levenberg_marquardt_1["default"](data, logisticFunction, options);
    return fittedParams;
}
/*
This allows the code to be used from the browser.
In addition, be sure to run "--s logistic" to expose the module.exports in the browser
under the global variable "logistic"!
*/
window.fit = fit;
window.logisticFunction = logisticFunction;
window.datesToNumbers = datesToNumbers;
module.exports = {
    fit: fit,
    logisticFunction: logisticFunction,
    datesToNumbers: datesToNumbers
};
