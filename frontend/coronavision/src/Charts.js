import React from 'react';

export default function Charts() {
    return (
        <>
            <h3>Charts</h3>
            <a id="download-chart" style={{display: "none"}}></a>
            <ChartOptions/>
            <div>
                <canvas id="chart"></canvas><br/>
                <button className="btn custom-button-color" onclick="download_canvas('chart')">Download world chart</button>
            </div>
        </>
    )
}

function ChartOptions() {
    return (
        <>
            <script src="/static/corona_chart_controller.js"></script>
            <select name="scale-type" className="custom-input-color form-control my-2">
                <option value="linear">Scale: Linear</option>
                <option value="logarithmic">Scale: Logarithmic</option>
            </select>
            <select name="chart-type" className="custom-input-color form-control my-2">
                <option value="total">Displaying: Total</option>
                <option value="daily-change">Displaying: Daily change</option>
            </select>
            <div className="form-check">
                <input type="checkbox" className="form-check-input" id="display-confirmed" name="display-confirmed" checked="checked"/>
                <label className="form-check-label" for="display-confirmed">
                    Display confirmed cases
                </label>
            </div>
            <div className="form-check">
                <input type="checkbox" className="form-check-input" id="display-deaths" name="display-deaths" checked="checked"/>
                <label className="form-check-label" for="display-deaths">
                    Display deaths
                </label>
            </div>
            <div className="form-check">
                <input type="checkbox" className="form-check-input" id="display-recovered" name="display-recovered" checked="checked"/>
                <label className="form-check-label" for="display-recovered">
                    Display recovered cases
                </label>
            </div>
            <div className="form-check">
                <input type="checkbox" className="form-check-input" id="display-active" name="display-active"/>
                <label className="form-check-label" for="display-active">
                    Display active cases
                </label>
            </div>
        </>
    )
}