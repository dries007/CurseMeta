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
 * @param a
 * @param b
 * @returns {number}
 */
function sortVersions(a, b) {
    a = splitNParse(a[0]);
    b = splitNParse(b[0]);
    while (a.length < b.length) a.push(0);
    while (b.length < a.length) b.push(0);
    for (var i = 0; i < a.length; i++) {
        if (a[i] === b[i]) continue;
        if (a[i] > b[i]) return 1;
        return -1;
    }
    return 0;
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
        table.sort({column: 1, desc: true});
    }
    var options = {
        title: title,
        tooltip: {isHtml: true, trigger: 'both'},
        height: 400,
        chartArea: {width: '90%', height: '90%'}
    };
    new google.visualization.PieChart($(id)[0]).draw(table, options);
}

/**
 * Sum all values of 2d object
 * @param obj `{type: {pid: downloads}}`
 * @returns {number}
 */
function sumTotal(obj) {
    var total = 0;
    types.forEach(function (t) {
        if (obj.hasOwnProperty(t)) {
            $.each(obj[t], function (id, dl) {
                total += dl;
            })
        }
    });
    return total;
}

/**
 * Sum 1 value of 2d object
 * @param obj `{type: {pid: downloads}}`
 * @param sub type
 * @returns {number}
 */
function sumPartial(obj, sub) {
    var total = 0;
    if (obj.hasOwnProperty(sub)) {
        $.each(obj[sub], function (id, dl) {
            total += dl;
        })
    }
    return total;
}

/**
 * Sum all types in 1d object
 * @param a `{type: number}`
 * @returns {number}
 */
function sumTypes(a) {
    var total = 0;
    types.forEach(function (t) {
        total += a[t];
    });
    return total;
}

/**
 * Count all values of 2d object
 * @param obj `{type: {pid: downloads}}`
 * @returns {number}
 */
function countTotal(obj) {
    var total = 0;
    types.forEach(function (t) {
        if (obj.hasOwnProperty(t)) {
            total += Object.keys(obj[t]).length;
        }
    });
    return total;
}

/**
 * Count 1 value of 2d object
 * @param obj `{type: {pid: downloads}}`
 * @param sub type
 * @returns {number}
 */
function countPartial(obj, sub) {
    if (obj.hasOwnProperty(sub)) {
        return Object.keys(obj[sub]).length
    }
    return 0;
}

/**
 * GLOBAL
 * @param header string
 * @param index string
 * @returns [...]
 */
function getDataType1(header, index) {
    var data = [['Project type', header, {type: 'string', role: 'tooltip', p: {html: true}}]];
    var total = sumTypes(DATA[index]);
    types.forEach(function (t) {
        var amount = DATA[index][t];
        data.push([
            t,
            amount,
            '<div class="tooltip">' +
                '<b>' + t + ':</b> ' + nf.format(amount) + '<br/>' +
                '<b>Total:</b> ' + nf.format(total) + '<br/>' +
                nf.format(amount*100/total) + '%<br/>' +
                '</div>'
        ]);
    });
    return data;
}

/**
 * DOWNLOADS - All
 * @param key key for each obj
 * @returns [..]
 */
function getDataType2(key) {
    var total_dl = sumTypes(DATA['downloads']);
    var total_prj = sumTypes(DATA['project_count']);
    var data = [['Username', 'Downloads', {type: 'string', role: 'tooltip', p: {html: true}}]];
    $.each(DATA['authors'], function (name, obj) {
        var downloads = 0; //sumTotal(obj[key]);
        var projects = 0; //countTotal(obj[key]);
        var projectsTable = '';

        types.forEach(function (t) {
            if (obj[key].hasOwnProperty(t)) {
                var o = obj[key][t];
                var pids = [];
                $.each(o, function (id, dl) {
                    downloads += dl;
                    projects += 1;
                    pids.push(id);
                });
                pids.sort(function (a, b) {
                   return o[b] - o[a];
                });
                pids.forEach(function (id) {
                    var dl = o[id];
                    var p = DATA['projects'][id];
                    projectsTable +=
                        '<tr>' +
                            '<td>' + p['name'] + '</td>' +
                            '<td>' + p['type'] + '</td>' +
                            '<td>' + nf.format(dl) + '</td>' +
                            '<td>' + nf.format(dl*100/total_dl) + '%</td>' +
                            '<td>' + nf.format(dl*100/downloads) + '%</td>' +
                        '</tr>';
                });
            }
        });

        data.push([
            name,
            downloads,
            '<div class="tooltip">' +
                '<b>' + name + ':</b> ' + nf.format(downloads) + '<br/>' +
                '<b>Total:</b> ' + nf.format(total_dl) + '<br/>' +
                nf.format(downloads*100/total_dl) + '%<br/>' +
                '<b>Projects:</b> ' + nf.format(projects) + ' (' + nf.format(projects*100/total_prj) + '%)' + '<br/>' +
                '<table>' +
                '<tr><th>Project</th><th>Type</th><th>Downloads</th><th>Global</th><th>Personal</th></tr>' +
                projectsTable + '</table>' +
            '</div>'
        ]);
    });
    return data;
}

/**
 * DOWNLOADS - Type specific
 * @param key key for each obj
 * @param type One of types.
 * @returns [..]
 */
function getDataType3(key, type) {
    var total = DATA['downloads'][type];
    var data = [['Username', 'Downloads', {type: 'string', role: 'tooltip', p: {html: true}}]];
    $.each(DATA['authors'], function (name, obj) {
        var downloads = sumPartial(obj[key], type);
        var projects = countPartial(obj[key], type);

        //todo

        data.push([
            name,
            downloads,
            '<div class="tooltip">' +
                '<b>' + name + ':</b> ' + nf.format(downloads) + '<br/>' +
                '<b>Total:</b> ' + nf.format(total) + '<br/>' +
                nf.format(downloads*100/total) + '%<br/>' +
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
    pieChart('#projects', 'Amount of projects', getDataType1('Number', 'project_count'), false);
    pieChart('#downloads', 'Amount of downloads', getDataType1('Downloads', 'downloads'), false);

    // Do sort, so the pies are going large to small
    pieChart('.dl .owned', 'Total Downloads (Owner only)', getDataType2('owner'), true);
    pieChart('.dl .member', 'Total Downloads (All members)', getDataType2('member'), true);

    pieChart('.dl .mod-owned', 'Mod Downloads (Owner only)', getDataType3('owner', types[0]), true);
    pieChart('.dl .mod-member', 'Mod Downloads (All members)', getDataType3('member', types[0]), true);

    pieChart('.dl .modpack-owned', 'Modpack Downloads (Owner only)', getDataType3('owner', types[1]), true);
    pieChart('.dl .modpack-member', 'Modpack Downloads (All members)', getDataType3('member', types[1]), true);

    // Start the mess
    // cols: Version, [type, tooltip]...
    var table = new google.visualization.DataTable();
    table.addColumn('string', 'Version');
    types.forEach(function (t) {
        table.addColumn('number', t);
        table.addColumn({type: 'string', role: 'tooltip', p: {html: true}});
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
        var name = d[0];
        var r = [name];
        var total_row = d[d.length - 1];
        // skip first (name), last(total_row)
        for (var i = 1; i < d.length - 1; i++) {
            var amount = d[i];
            r.push(amount);
            r.push('<div class="tooltip">' +
                '<b>' + name + '</b><br/>' +
                '<b>' + types[i-1] + ':</b> ' + nf.format(amount) + '<br/>' +
                '<b>Total:</b> ' + nf.format(total_row) + '<br/>' +
                nf.format(amount*100/total_row) + '% of ' + name + '<br/>' +
                nf.format(amount*100/total) + '% of total' +
                '</div>')
        }
        table.addRow(r);
    });

    var options = {
        title: 'Projects per MC version',
        isStacked: true,
        tooltip: {isHtml: true, trigger: 'both'},
        height: 400,
        chartArea: {left: 75, bottom: 70, width: '85%', height: '75%'}

    };
    new google.visualization.ColumnChart($('#versions')[0]).draw(table, options);

    $(function () {

        $('#total-projects').text(sumTypes(DATA['project_count']));
        $('#total-downloads').text(sumTypes(DATA['downloads']));
        $('#total-authors').text(Object.keys(DATA['authors']).length);

        $('#loading').remove();
    })
}

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
    crossDomain: true,
    url: URL_BASE + "stats.json",
    cache: false,
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
