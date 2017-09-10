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
 * Originally: `Object.keys(DATA['projects']);`
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
 * @param id Element ID
 * @param title Title string
 * @param data [[header, ...], [data, ...], ...]
 * @param sort {boolean}
 */
function pieChart(id, title, data, sort) {
    var table = google.visualization.arrayToDataTable(data, false);
    if (sort) {
        table.sort({column: 1, desc: true});
    }
    table.addColumn({type: 'string', role: 'tooltip', p: {html: true}});

    var total = 0;
    for (var i = 0; i < table.getNumberOfRows(); i++) {
        total += table.getValue(i, 1)
    }
    for (var i = 0; i < table.getNumberOfRows(); i++) {
        var name = table.getValue(i, 0);
        var amount = table.getValue(i, 1);
        var tooltip = '<div class="tooltip"><b>' + name + ':</b> ' + nf.format(amount) + '<br/>' + nf.format(amount*100/total) + '%</div>';
        table.setCell(i, 2, tooltip)
    }

    var options = {
        title: title,
        tooltip: {isHtml: true},
        height: 400,
        chartArea: {width: '90%', height: '90%'}
    };
    new google.visualization.PieChart($('#' + id)[0]).draw(table, options);
}

/**
 * MAIN
 */
function run() {
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
     * Project Type
     * @param header string
     * @param index string
     * @returns [...]
     */
    function getDataType1(header, index) {
        var data = [['Project type', header]];
        types.forEach(function (t) {
            data.push([t, DATA[index][t]]);
        });
        return data;
    }

    /**
     * @param key key for each obj
     * @param f function
     * @param args extra f args
     * @returns [..]
     */
    function getDataType2(key, f, args) {
        var data = [
            ['Username', 'Downloads']
        ];
        $.each(DATA['authors'], function (name, obj) {
            var a = [obj[key]];
            a.push(args || []);
            data.push([name, f.apply(this, a)]);
        });
        return data;
    }

    pieChart('projects', 'Amount of projects', getDataType1('Number', 'projects'), false);
    pieChart('downloads', 'Amount of downloads', getDataType1('Downloads', 'downloads'), false);

    pieChart('owned', 'Total Downloads (Owner only)', getDataType2('owner', sumTotal), true);
    pieChart('member', 'Total Downloads (All members)', getDataType2('member', sumTotal), true);

    pieChart('mod-owned', 'Mod Downloads (Owner only)', getDataType2('owner', sumPartial, 'Mods'), true);
    pieChart('mod-member', 'Mod Downloads (All members)', getDataType2('member', sumPartial, 'Mods'), true);

    pieChart('modpack-owned', 'Mod Downloads (Owner only)', getDataType2('owner', sumPartial, 'Modpacks'), true);
    pieChart('modpack-member', 'Mod Downloads (All members)', getDataType2('member', sumPartial, 'Modpacks'), true);

    var table = new google.visualization.DataTable();
    table.addColumn('string', 'Version');
    types.forEach(function (t) {
        table.addColumn('number', t);
        table.addColumn({type: 'string', role: 'tooltip', p: {html: true}});
    });
    var data = [];
    var total = 0;
    $.each(DATA['version'], function (name, obj) {
        var total_row = 0;
        var row = [name];
        types.forEach(function (t) {
            if (obj.hasOwnProperty(t)) {
                row.push(obj[t]);
                total_row += obj[t];
            } else {
                row.push(0);
            }
        });
        total += total_row;
        row.push(total_row);
        data.push(row);
    });
    data.sort(sortVersions); // sort based on version string
    data.forEach(function (d) { // tooltip stuff
        var name = d[0];
        var r = [name];
        var total_row = d[d.length - 1];
        // skip first (name), last(total)
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
        tooltip: {isHtml: true},
        height: 400,
        chartArea: {left: 75, bottom: 70, width: '85%', height: '75%'}

    };
    new google.visualization.ColumnChart($('#versions')[0]).draw(table, options);
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
