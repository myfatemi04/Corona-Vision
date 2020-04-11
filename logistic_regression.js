let X = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0];
let Y = X.map((val) => 1/(1 + Math.pow(Math.E, -0.05 * val))); // base function

function predict(x, equation) {
    return (equation.K) / (1 + (equation.B) * Math.pow(Math.E, -(x * (equation.r))));
}

// optimize squared error
function cost(equation, X, Y) {
    let sum = 0;
    for (let v = 0; v < X.length; v++) {
        sum += Math.abs(predict(X[v], equation) - Y[v]);
    }
    return sum / X.length;
}

function sub(equation, property, value) {
    let ret = {};
    for (let key in equation) {
        if (key == property) ret[key] = value;
        else {
            ret[key] = equation[key];
        }
    }
    return ret;
}

// Returns logistic regression curve equation
function logreg(X, Y) {
    let equation = {
        K: Math.max(...Y),// population cap
        B: 1,// some coefficient
        r: 1 // coefficient of exponent
    };

    let epochs = 40;
    let delta = 0.00003;
    let learn_rate = 0.03;

    for (let i = 0; i < epochs; i++) {
        let e_cost = cost(equation, X, Y);
        let next_equation = {

        };

        for (let property in equation) {
            let next_cost = cost(sub(equation, property, equation[property] + delta), X, Y);
            let d_cost = (next_cost - e_cost) / delta;
            let direction = learn_rate * -d_cost/4;
            next_equation[property] = equation[property] + direction;
            //console.log(property, d_cost, direction);
        }

        if (epochs < 500)
            console.log(e_cost);

        equation = next_equation;

        // let best_K = minimize(equation.K * 0.9, equation.K * 1.1, (k) => cost({K: k, B: equation.B, r: equation.r}, X, Y), 4);
        // let best_B = minimize(equation.B * 0.9, equation.B * 1.1, (b) => cost({K: equation.K, B: b, r: equation.r}, X, Y), 4);
        // let best_r = minimize(equation.r * 0.9, equation.r * 1.1, (r) => cost({K: equation.K, B: equation.B, r: r}, X, Y), 4);
        
        // equation.K = best_K;
        // equation.B = best_B;
        // equation.r = best_r;
    }       

    return equation;
}

function minimize(min_val, max_val, cost, iter_left) {
    if (iter_left == 0) return (min_val + max_val) / 2;
    let segments = 10;
    let mid = (min_val + max_val) / 2;
    let range = max_val - min_val;
    let min_min = min_val;
    let min_max = max_val;
    let min_cost = cost((min_val + max_val) / 2);
    for (let i = min_val; i < max_val; i += range/segments) {
        let c = cost(i + 0.5 * range/segments);
        if (c < min_cost) {
            min_cost = c;
            min_min = i;
            min_max = i + range/segments;
        }
    }
    return minimize(min_min, min_max, cost, iter_left - 1);
}

function test() {
    let fs = require("fs");
    let csv = fs.readFileSync("test_data_2.csv", "utf-8");
    let lines = csv.split("\n");
    let X2 = [];
    let Y2 = [];
    for (let i = 1; i < lines.length; i++) {
        let row = lines[i].split(",");
        X2.push(parseInt(row[0]));
        Y2.push(parseInt(row[1]));
    }
    equation = logreg(X2, Y2);
    console.log(cost(equation, X2, Y2));
    console.log(equation);
}

test();
