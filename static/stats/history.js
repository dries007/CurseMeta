/**
    Copyright 2017 Dries007

    Licensed under the EUPL, Version 1.1 only (the "Licence");
    You may not use this work except in compliance with the Licence.
    You may obtain a copy of the Licence at:

    https://joinup.ec.europa.eu/software/page/eupl5

    Unless required by applicable law or agreed to in writing, software
    distributed under the Licence is distributed on an "AS IS" basis,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the Licence for the specific language governing
    permissions and limitations under the Licence.
 */

"use strict";

console.info("Copyright 2017 Dries007 - Licensed under the EUPL v1.1 - https://github.com/dries007/curseMeta");

var URL_BASE = "https://cursemeta.dries007.net/";

var HISTORY;
var STATS;
var DATA = {};
var LIMIT = parseInt(URIHash.get('limit')) || 500;
var POINTS = parseInt(URIHash.get('points')) || 150;
var START = parseInt(URIHash.get('start')) || Math.floor((Date.now()/1000) - (30 * 24 * 60 * 60));

function toInt(t) {
    return parseInt(t);
}

function sortByDownloads(a, b) {
    return STATS['projects'][b]['downloads'] - STATS['projects'][a]['downloads'];
}

function mapIdToName(id) {
    return STATS['projects'][id]['name'];
}

function updateLimit(limit) {
    URIHash.set('limit', limit);
    LIMIT = parseInt(limit);
    draw();
}

function updateStart(start) {
    URIHash.set('start', start);
    START = parseInt(start);
    run();
}

function updatePoints(points) {
    URIHash.set('points', points);
    START = parseInt(points);
    run();
}

function draw() {
    $('#loading').show();
    setTimeout(function () {
        var keys = Object.keys(DATA).map(toInt).sort();
        var projects = Object.keys(STATS['projects']).sort(sortByDownloads);
        if (LIMIT !== 0) {
            projects = projects.slice(0, LIMIT);
        }
        var data = [[{type: 'datetime', id: 'time', label: 'Time', format: 'long'}].concat(projects.map(mapIdToName))];
        keys.forEach(function (timestamp) {
            data.push([new Date(timestamp * 1000)].concat(projects.map(function (id) {return DATA[timestamp][id]})));
        });

        var table = google.visualization.arrayToDataTable(data);
        var options = {
            title: 'Downloads',
            vAxis: { format: 'short' },
            chartArea: {left: 75, bottom: 25, top: 25, right: 200} // magic numbers YEY
        };
        new google.visualization.LineChart($('#timeline')[0]).draw(table, options);
        $('#loading').hide();
    }, 1);
}

/**
 * MAIN
 */
function run() {
    DATA = {};

    // do ALL of the requests at once
    var requests = [];
    var n = 0;
    HISTORY.forEach(function (t) {
        if (t < START) return;
        n++;
        requests.push($.ajax({
            type: 'GET',
            url: URL_BASE + 'history/' + t + '.json',
            dataType: 'json',
            success: function(data) {
                DATA[t] = data
            }
        }));
    });
    // reduce to POINTS requests
    if (n > POINTS) {
        // thanks https://stackoverflow.com/a/2451363/4355781
        var step = (n - 1) / (POINTS - 1);
        var requests_ = [];
        for (var i = 0; i < POINTS; i ++) {
            requests_.push(requests[Math.round(step * i)]);
        }
        requests = requests_;
    }
    console.info('Requesting ' + requests.length + ' datapoints.');
    // When every request is done
    $.when.apply(undefined, requests).done(draw);
}

$(function () {
    $('#limit').val(LIMIT);
    $('#start').val(START);
    $('#points').val(POINTS);

    var loaded = 3;

    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(function () {
        loaded -= 1;
        if (loaded === 0) {
            run();
        }
    });

    $.ajax({
        type: 'GET',
        url: URL_BASE + 'stats.json',
        dataType: 'json',
        success: function(data) {
            STATS = data['stats'];
            loaded -= 1;
            if (loaded === 0) {
                run();
            }
        }
    });

    $.ajax({
        type: 'GET',
        url: URL_BASE + 'history/index.json',
        dataType: 'json',
        success: function(data) {
            $('#timestamp').text(data['timestamp_human']);
            HISTORY = data['history'];
            loaded -= 1;
            if (loaded === 0) {
                run();
            }
        }
    });
});
