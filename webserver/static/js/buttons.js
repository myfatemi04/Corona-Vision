function fallbackCopyTextToClipboard(text) {
    var textArea = document.createElement("textarea");
    textArea.value = text;

    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        var successful = document.execCommand('copy');
        var msg = successful ? 'successful' : 'unsuccessful';
        console.log('Fallback: Copying text command was ' + msg);
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }

    document.body.removeChild(textArea);
}
function copyTextToClipboard(text) {
    if (!navigator.clipboard) {
        fallbackCopyTextToClipboard(text);
        return;
    }
    navigator.clipboard.writeText(text).then(function() {
        console.log('Async: Copying to clipboard was successful!');
    }, function(err) {
        console.error('Async: Could not copy text: ', err);
    });
}

function copyLink(country='', province='', county='') {
    let linkHref = `https://coronavision.us/`;
    if (country) {
        linkHref += '?country=' + country;
        if (province) {
            linkHref += '&province=' + province;
            if (county) {
                linkHref += '&county=' + county;
            }
        }
    }
    copyTextToClipboard(linkHref);
}

function setDate() {
    window.location = "?country={{country}}&province={{province}}&county={{county}}&date=" + $("#date").val();
}

function setCountry() {
    window.location = "?country=" + $("#countrySelector").val() + "&date={{entry_date}}";
}

function setProvince() {
    window.location = "?country=" + country + "&province=" + $("#provinceSelector").val() + "&date={{entry_date}}";
}

function setCounty() {
    window.location = "?country=" + country + "&province=" + province + "&county=" + $("#countySelector").val() + "&date={{entry_date}}";
}

function goYesterday() {
    $("#date")[0].selectedIndex += 1;
    $("#date").trigger("change");
}

function goTomorrow() {
    $("#date")[0].selectedIndex -= 1;
    $("#date").trigger("change");
}

function viewPredictions() {
    window.location = "/future?country=" + country + "&province=" + province + "&county=" + county;
}