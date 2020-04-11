const {spawn} = require('child_process');
const cache = {

};

const python = spawn('python', ['corona_predictor.py', '1 2 3 4', '2 4 8 16', '4']);
python.stdout.on("data", function(data) {
    console.log("Piping data...");
    console.log(data.toString());
});

python.stderr.on("data", function(data) {
    console.log("Error!");
    console.log(data.toString());
});

python.on('close', (code) => {
    console.log("Child process closed");
});


