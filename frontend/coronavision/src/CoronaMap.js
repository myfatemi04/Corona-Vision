import React from 'react';
import Stats from './Stats.js';
import Charts from './Charts.js';

function CoronaMapContainer() {
    return (
        <div className="container-fluid">
			<div className="container-fluid box dashboard-container py-2">
				<div className="map-box scroll dash-4 mx-1">
					<CoronaMap />
				</div>
                <div className="scroll dash-2 mx-1">
				    <StatsColumn />
                </div>
			</div>
		</div>
    )
}

function CoronaMap() {
    return (
        <>
            <h3>Map
                <a style={{fontSize: "0.5rem"}} href="https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports">
                    Source
                </a>
            </h3>
            <div className="d-flex flex-column">
                <noscript>
                    This website requires JavaScript to run.
                </noscript>
                <select name="map-type" className="custom-input-color form-control my-2">
                    <option value="total">Total</option>
                    <option value="daily-change">Change since yesterday</option>
                </select>
                <select name="map-display" className="custom-input-color form-control my-2">
                    <option value="active">Active cases</option>
                    <option value="confirmed">Confirmed cases</option>
                    <option value="recovered">Recovered cases</option>
                    <option value="dead">Deaths</option>
                </select>
                <select className="custom-input-color form-control my-2" id="date" onchange="reload_cases();" onload="load_dates();">
                </select>
            </div>
            <div className="mb-bot">
                <div id="map" className="map my-2"></div>
            </div>
        </>
    )
}

function StatsColumn() {
    return (
        <>
            <div className="d-flex flex-column">
                <Stats/>
            </div>
            <hr className="custom-hr"/>
            <div className="d-flex flex-column">
                <Charts/>
            </div>
        </>
    )
}

export default CoronaMapContainer;