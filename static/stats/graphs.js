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
// var URL_BASE = "http://localhost:63342/curseMeta/www/"; // todo: remove before commit

/**
 * Manually coded to preserve consistent key order.
 * Originally: `Object.keys(DATA['project_count']);`
 * @type {[string,string,string,string]}
 */
var types = ['Mods', 'Modpacks', 'Texture Packs', 'Worlds'];
var nf = new Intl.NumberFormat(undefined, {maximumFractionDigits: 2});

var DATA;
var CHARTS = [];

/**
 * Clear the selection of all graphs, to hide the tooltips.
 */
function nukeTooltips() {
    CHARTS.forEach(function (t) {
        t.setSelection([{}]); // Thanks stackoverflow
    })
}

/**
 * Split version string (n.m[.p, ...]) into a int array
 * @param str
 * @returns {Array}
 */
function splitNParse(str) {
    var o = [];
    str.split('.').forEach(function (t) {
        o.push(parseInt(t));
    });
    return o;
}

/**
 * Comparator for version strings, can handle different length version ids
 * a[0], b[0] contain version strings because input is one row of table .([[version, data, ...], ...])
 * Lowest version first
 * @param a
 * @param b
 * @returns {number}
 */
function sortVersions(a, b) {
    a = splitNParse(a[0]); // a and b are rows of table, version strings are in col 0
    b = splitNParse(b[0]);
    while (a.length < b.length) a.push(0); // Fill with zeroes, so 1.0 can be compared to 1.0.1
    while (b.length < a.length) b.push(0);
    for (var i = 0; i < a.length; i++) {
        if (a[i] === b[i]) continue;
        if (a[i] > b[i]) return 1;
        return -1;
    }
    return 0;
}

/**
 * High to low dl count, uses global project data
 * @param a pid
 * @param b pid
 * @returns {number}
 */
function sortByDownloads(a, b)
{
    return DATA['projects'][b]['downloads'] - DATA['projects'][a]['downloads'];
}

/**
 * @param id {selector} Element ID
 * @param title Title string
 * @param data [[header, ...], [data, ...], ...]
 * @param sort {boolean}
 */
function pieChart(id, title, data, sort) {
    var table = google.visualization.arrayToDataTable(data, false);
    if (sort) {
        table.sort({column: 1, desc: true}); // not col 0, that is the name.
    }
    var options = {
        title: title,
        tooltip: {isHtml: true, trigger: 'both'}, // both allows tooltips to stay
        height: 400,
        chartArea: {width: '90%', height: '90%'} // make graph occupy more of the space
    };
    var chart = new google.visualization.PieChart($(id)[0]);
    chart.draw(table, options);
    CHARTS.push(chart); // keep ref so we can nuke tooltips later
}

/**
 * Sum all types in 1d object
 * @param a `{type: number}`
 * @param types [string] every type that needs to be added
 * @returns {number}
 */
function sumTypes(a, types) {
    var total = 0;
    types.forEach(function (t) {
        if (a.hasOwnProperty(t)) {
            total += a[t];
        }
    });
    return total;
}

function tooltipLine(name, amount, total) {
    return '<b>' + name + ':</b> ' + nf.format(amount) + ' (' + nf.format(amount*100/total) +'% of ' +  nf.format(total) + ')'
}

/**
 * GLOBAL
 * @param header string
 * @param index string
 * @returns [...]
 */
function getGlobalData(header, index) {
    var data = [['Project type', header, {type: 'string', role: 'tooltip', p: {html: true}}]]; // pre-add header row
    var total = sumTypes(DATA[index], types);
    types.forEach(function (t) { // loop over types to preserve order
        var amount = DATA[index][t];
        data.push([t, amount, '<div class="tooltip">' + tooltipLine(t, amount, total) + '</div>']);
    });
    return data;
}

/**
 * DOWNLOADS
 * @param key key for each obj
 * @param types [string] every type that needs to be added
 * @returns [..]
 */
function getPersonalData(key, types) {
    var total_dl = sumTypes(DATA['downloads'], types);
    var total_prj = sumTypes(DATA['project_count'], types);
    var data = [['Username', 'Downloads', {type: 'string', role: 'tooltip', p: {html: true}}]]; // pre-add header row
    $.each(DATA['authors'], function (name, obj) {
        var downloads = 0;
        var projects = 0;
        var projectsTable = '';
        types.forEach(function (t) { // loop over types to preserve order for tooltip table
            if (obj[key].hasOwnProperty(t)) {
                var pids = obj[key][t]; // array of pids
                projects += pids.length;
                pids.sort(sortByDownloads);
                pids.forEach(function (id) { // calc dl count
                    downloads += DATA['projects'][id]['downloads']
                });
                pids.forEach(function (id) { // tooltip table row
                    var p = DATA['projects'][id];
                    projectsTable +=
                        '<tr data-pid="' + id + '">' +
                            '<td>' + p['name'] + '</td>' +
                            '<td>' + p['type'] + '</td>' +
                            '<td>' + nf.format(p['downloads']) + '</td>' +
                            '<td>' + nf.format(p['downloads']*100/total_dl) + '%</td>' +
                            '<td>' + nf.format(p['downloads']*100/downloads) + '%</td>' +
                        '</tr>';
                });
            }
        });

        data.push([
            name,
            downloads,
            '<div class="tooltip">' +
                '<b>' + name + '</b><br/>' +
                tooltipLine("Downloads", downloads, total_dl) + '<br/>' +
                tooltipLine("Projects", projects, total_prj) + '<br/>' +
                '<table><tr><th>Project</th><th>Type</th><th>Downloads</th><th>Global</th><th>Personal</th></tr>' + projectsTable + '</table>' +
            '</div>'
        ]);
    });
    return data;
}

/**
 * MAIN
 */
function run() {
    // Don't sort the project lists, so the order (and thus colors) is consistent
    pieChart('#projects', 'Amount of projects', getGlobalData('Number', 'project_count'), false);
    pieChart('#downloads', 'Amount of downloads', getGlobalData('Downloads', 'downloads'), false);

    // Do sort, so the pies are going large to small
    pieChart('.dl .owned', 'Total Downloads (Owner only)', getPersonalData('owner', types), true);
    pieChart('.dl .member', 'Total Downloads (All members)', getPersonalData('member', types), true);

    pieChart('.dl .mod-owned', 'Mod Downloads (Owner only)', getPersonalData('owner', [types[0]]), true);
    pieChart('.dl .mod-member', 'Mod Downloads (All members)', getPersonalData('member', [types[0]]), true);

    pieChart('.dl .modpack-owned', 'Modpack Downloads (Owner only)', getPersonalData('owner', [types[1]]), true);
    pieChart('.dl .modpack-member', 'Modpack Downloads (All members)', getPersonalData('member', [types[1]]), true);

    // Start the mess (stacked col graph)
    // cols: Version, [type, tooltip]...
    var table = new google.visualization.DataTable();
    table.addColumn('string', 'Version'); // X axis
    types.forEach(function (t) {
        table.addColumn('number', t); // data
        table.addColumn({type: 'string', role: 'tooltip', p: {html: true}}); // tooltip
    });
    var data = []; // Cannot be stored directly in a table because we need to sort later
    var total = 0; // Global total
    $.each(DATA['version'], function (name, obj) {
        var total_row = 0; // Total per version (=row)
        var row = [name]; // Populate the Version col
        types.forEach(function (t) {
            if (obj.hasOwnProperty(t)) { // Not every version has all types
                row.push(obj[t]);
                total_row += obj[t];
            } else {
                row.push(0); // Must include 0 for table to be consistent
            }
        });
        total += total_row;
        row.push(total_row); // Store for tooltips, can't do them here already because they need the total.
        data.push(row);
    });
    data.sort(sortVersions); // sort based on version string
    data.forEach(function (d) { // tooltip stuff
        var version = d[0];
        var r = [version];
        var total_row = d[d.length - 1];
        // skip first (version), last(total_row)
        for (var i = 1; i < d.length - 1; i++) {
            var amount = d[i];
            r.push(amount);
            r.push('<div class="tooltip">' +
                tooltipLine(version, total_row, total) + '<br/>' +
                tooltipLine(types[i-1], amount, total_row) + '<br/>' +
                '</div>')
        }
        table.addRow(r);
    });

    var options = {
        title: 'Projects per MC version',
        isStacked: true,
        tooltip: {isHtml: true, trigger: 'both'}, // Pop up tooltips
        height: 400,
        chartArea: {left: 75, bottom: 70, width: '85%', height: '75%'} // magic numbers YEY

    };
    var chart = new google.visualization.ColumnChart($('#versions')[0]);
    chart.draw(table, options);
    CHARTS.push(chart);

    $('#total-projects').text(nf.format(sumTypes(DATA['project_count'], types)));
    $('#total-downloads').text(nf.format(sumTypes(DATA['downloads'], types)));
    $('#total-authors').text(nf.format(Object.keys(DATA['authors']).length));

    $('#loading').remove();
}

$(function () {
    var isLoadedCharts = false;
    var isLoadedData = false;

    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(function () {
        isLoadedCharts = true;
        if (isLoadedData) {
            run();
        }
    });

    $.ajax({
        type: "GET",
        url: URL_BASE + "stats.json",
        dataType: "json",
        success: function(data) {
            $('#timestamp').text(data["timestamp_human"]);
            DATA = data['stats'];
            isLoadedData = true;
            if (isLoadedCharts) {
                run();
            }
        }
    });
});
