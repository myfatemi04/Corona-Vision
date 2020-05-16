import * as express from "express";
import { registerPartials, getRouter } from "./webapp";

const hostname = '0.0.0.0';
const port = process.env.PORT || 4040;

let app = express();

app.set('view engine', 'hbs'); // we are using Handlebars
registerPartials();

app.use(express.static('static')); // static content, such as images and CSS, is served through here
app.use("/", getRouter());

app.listen(port, () => console.log(`Server started at ${hostname}:${port}!`));

