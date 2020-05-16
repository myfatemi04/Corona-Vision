# Welcome to Coronavision!
This app was intended to help people track the spread of the coronavirus and visualize its spread using graphs and animated heatmaps. I wrote this in 10th grade, with some help from some of my friends.

# Features

## Live Data
I used a web-scraping library called Beautiful Soup to scrape coronavirus statistics from several government websites and news sources. This was very difficult, as I wanted to collect state-level data for several countries including the US, Italy, France, China, South Korea, Portugal, Spain, Argentina, and many more.
### Collecting the data
Some of this data was easy to parse, as many news sources, like Canada and Germany, used JSON APIs to load their data dynamically to their websites, and many countries, such as Portugal, used ArcGIS databases which had REST APIs, but others were much more difficult, such as Argentina, who reported state-level cases via PDF files.
### Storing the data
I used a MySQL database connected to Google Cloud to store the data. The basic schema stored an entry date, a country, a province, a county, and total cases / deaths / recoveries along with each data point. To access the database on the webserver, I used `mysql`, and to upload data from the data collection backend, I used `SQLAlchemy`.
## Maps
I included state-level maps for every country I collected data for. In addition, I included an overall world map, and a case heatmap.
### Color Maps
I used SVG maps for this part, because they included country borders out-of-the box, and could easily be styled with hover events and fills via jQuery.
### Heatmap
The heatmaps depended more on geographic points, so I couldn't use SVG maps. To make this, I first collected location data for the countries and their states and counties. Then, I used the Google Maps Javascript SDK using each location's latitude, longitude, and intensity as a feature layer. 
## Charts
The charts were available for all countries and states, and graphed a 7-day moving average trendline along with the raw data. Originally, I included a logistic regression to attempt to predict the spread of the virus, and it fit the data correctly, but it became clear that the logistic predictions weren't accurate for the long-term. To prevent misinformation, I hid them from the site.
## News
I used the [News API](newsapi.org) to add live news coverage of the virus.
# How To Run
The website frontend runs on NodeJS. To start the frontend server:
1. Install NodeJS, if you haven't already
2. Navigate to the `webserver/` directory
3. `npm i` to install the dependencies
4. `npm start` to start the site

Then, you can navigate to `localhost:4040` in your browser to access the website.
The data collection backend probably will be outdated in a few years, but you can run it by doing this:
1. Install Python 3.7 if you haven't already
2. Install the dependencies by running `pip install -r requirements.txt`
3. Run with `python server.py`.

!!NOTE: you may receive an error relating to SQL. **This is because you need to specify a database.** To use the database snapshot from May 8th, 2020, change the database url to `sqlite:///SnapshotMay8th.db` in `data_collection/corona_sql.py` and  `webserver/corona_sql.ts`. Then, run `tsc` in the `webserver` directory to recompile the files. If you don't have `tsc`, do `npm install -g typescript` to install it globally.
Soon, I will make a mode where it will do this automatically for you.
Thanks for reading!
If you have any questions then reach out to me at myfatemi04@gmail.com.
