import React from 'react'

function Stats() {
    return (
        <>
            <h3>Stats</h3>
            <Selectors/>
            <div id="stats-info"></div>
        </>
    );
}

function Selectors() {
    return (
        <>
            <select id="country-selector" class="custom-input-color form-control my-2">
                <option value="">Whole world</option>
            </select>
            <select id="province-selector" class="custom-input-color form-control my-2" disabled>
                <option value="">Whole country</option>
            </select>
            <select id="admin2-selector" class="custom-input-color form-control my-2" disabled>
                <option value="">Whole state</option>
            </select>
        </>
    );
}

export default Stats;