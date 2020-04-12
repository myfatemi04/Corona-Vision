const {spawn} = require('child_process');
const cache = {

};

let dates = '2020-01-22 2020-01-23 2020-01-24 2020-01-25 2020-01-26 2020-01-27 2020-01-28 2020-01-29 2020-01-30 2020-01-31 2020-02-01 2020-02-02 2020-02-03 2020-02-04 2020-02-05 2020-02-06 2020-02-07 2020-02-08 2020-02-09 2020-02-10 2020-02-11 2020-02-12 2020-02-13 2020-02-14 2020-02-15 2020-02-16 2020-02-17 2020-02-18 2020-02-19 2020-02-20 2020-02-21 2020-02-22 2020-02-23 2020-02-24 2020-02-25 2020-02-26 2020-02-27 2020-02-28 2020-02-29 2020-03-01 2020-03-02 2020-03-03 2020-03-04 2020-03-05 2020-03-06 2020-03-07 2020-03-08 2020-03-09 2020-03-10 2020-03-11 2020-03-12 2020-03-13 2020-03-14 2020-03-15 2020-03-16 2020-03-17 2020-03-18 2020-03-19 2020-03-20 2020-03-21 2020-03-22 2020-03-23 2020-03-24 2020-03-25 2020-03-26 2020-03-27 2020-03-28 2020-03-29 2020-03-30 2020-03-31 2020-04-01 2020-04-02 2020-04-03 2020-04-04 2020-04-05 2020-04-06 2020-04-07 2020-04-08 2020-04-09 2020-04-10';
let confirmed = '1 1 2 2 5 5 5 5 5 6 8 8 11 11 12 12 12 12 12 12 13 13 15 15 15 15 15 15 15 15 35 35 35 53 53 59 60 62 70 76 101 122 153 221 278 417 537 605 959 1281 1663 2179 2726 3499 4632 6421 7786 13680 19101 25514 33848 43667 53740 65778 83836 101657 121465 140909 161831 188172 213372 243599 275586 308853 337072 366667 396223 429052 461437 496535';

if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function() 
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

module.exports = {
    logfit: get_logistic
};

function get_logistic(key, dates, confirmed) {
    console.log("Running logfit...");
    // confirmed = smooth_data(confirmed.split(" ").map((a) => parseFloat(a)), 0).join(" ");
    return new Promise(function(resolve, reject) {
        if (key in cache && Date.now() - cache[key].time < (10 * 60 * 1000)) {
            console.log("Returned cached version");
            resolve(cache[key].json);
            return;
        } else {
            cache[key] = {};
        }
    
        const python = spawn('python', ['corona_predictor.py', dates, confirmed, '4']);
        python.stdout.on("data", function(data) {
            if (data.toString().startsWith("data=")) {
                cache[key].json = JSON.parse(data.toString().substring(5));
                cache[key].time = Date.now();
                console.log("Complete")
                resolve(cache[key].json);
            } else {
                console.log(data.toString());
            }
        });

        python.stderr.on("data", function(data) {
            console.log("Err: ", data.toString());
        });
    });
}

function smooth_data(array, smoothing=0) {
	// smoothing is too high
	if (smoothing > array.length - 1) {
		smoothing = array.length - 1;
	}

	// now, we use a map function
	let smooth_array = array.map((value, index) => {
		// at a certain index, take the values N days before and N days after
		let taken_left = Math.min(smoothing, index);
		let taken_right = Math.min(smoothing, (array.length - 1 - index));
		let taken_center = 1;
		let total = taken_left + taken_right + taken_center;
		let values = array.slice(index - taken_left, index + taken_right + 1);
		let sum = values.reduce((a, b) => (a + b));

		let missing_right = (smoothing - taken_right);
		let missing_left = (smoothing - taken_left);

		sum += missing_right * array[array.length - 1];
		sum += missing_left * array[0];

		return sum / (2 * smoothing + 1);
	});

	return smooth_array;
}