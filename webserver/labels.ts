function getLabel(country?: string, province?: string, county?: string) {
    let label = "World";
    if (!country) return label;
    label = country;
    if (!province) return label;
    label = province + ", " + label;
    if (!county) return label;
    label = county + ", " + label;
    return label;
}

function getChildLabel(country?: string, province?: string, county?: string) {
    if (!country) return "country";
    if (!province) return "province";
    if (!county) return "county";
}

export {
    getLabel,
    getChildLabel
};