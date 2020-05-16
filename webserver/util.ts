function utc_iso(date) {
    if (typeof date == "undefined") {
        return utc_iso(new Date());
    }
    if (typeof date == "string") {
        return date;
    }
    let year = date.getUTCFullYear();
    let month = `${date.getUTCMonth() + 1}`;
    let day = `${date.getUTCDate()}`;
    month = month.padStart(2, "0");
    day = day.padStart(2, "0");
    return year + "-" + month + "-" + day;
}

export {
    utc_iso
};