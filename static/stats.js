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

var isLoadedCharts = false;
var isLoadedData = false;
var DATA;

function run() {
    var types = Object.keys(DATA['projects']);

    var table = new google.visualization.DataTable();
    table.addColumn('string', 'Project type');
    table.addColumn('number', 'Number');
    $.each(DATA['projects'], function (name, amount) {
        table.addRow([name, amount]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#projects')[0]).draw(table, {title: 'Amount of projects'});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Project type');
    table.addColumn('number', 'Downloads');
    $.each(DATA['downloads'], function (name, amount) {
        table.addRow([name, amount]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#downloads')[0]).draw(table, {title: 'Amount of downloads'});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Version');
    types.forEach(function (t) {
        table.addColumn('number', t);
    });
    $.each(DATA['version'], function (name, obj) {
        var row = [name];
        types.forEach(function (t) {
            if (obj.hasOwnProperty(t)) {
                row.push(obj[t])
            } else {
                row.push(0)
            }
        });
        table.addRow(row);
    });
    table.sort({column: 0});
    new google.visualization.ColumnChart($('#versions')[0]).draw(table, {title: 'Projects per MC version', isStacked: true});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Username');
    table.addColumn('number', 'Downloads');
    $.each(DATA['authors'], function (name, obj) {
        obj = obj['owner'];
        var total = 0;
        types.forEach(function (t) {
            if (obj.hasOwnProperty(t)) {
                $.each(obj[t], function (id, dl) {
                    total += dl;
                })
            }
        });
        table.addRow([name, total]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#owned')[0]).draw(table, {title: 'Total Downloads (Owner only)'});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Username');
    table.addColumn('number', 'Downloads');
    $.each(DATA['authors'], function (name, obj) {
        obj = obj['member'];
        var total = 0;
        types.forEach(function (t) {
            if (obj.hasOwnProperty(t)) {
                $.each(obj[t], function (id, dl) {
                    total += dl;
                })
            }
        });
        table.addRow([name, total]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#member')[0]).draw(table, {title: 'Total Downloads (All members)'});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Username');
    table.addColumn('number', 'Downloads');
    $.each(DATA['authors'], function (name, obj) {
        obj = obj['owner'];
        var total = 0;
        if (obj.hasOwnProperty('Mods')) {
            $.each(obj['Mods'], function (id, dl) {
                total += dl;
            })
        }
        table.addRow([name, total]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#mod-owned')[0]).draw(table, {title: 'Mod Downloads (Owner only)'});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Username');
    table.addColumn('number', 'Downloads');
    $.each(DATA['authors'], function (name, obj) {
        obj = obj['member'];
        var total = 0;
        if (obj.hasOwnProperty('Mods')) {
            $.each(obj['Mods'], function (id, dl) {
                total += dl;
            })
        }
        table.addRow([name, total]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#mod-member')[0]).draw(table, {title: 'Mod Downloads (All members)'});


    table = new google.visualization.DataTable();
    table.addColumn('string', 'Username');
    table.addColumn('number', 'Downloads');
    $.each(DATA['authors'], function (name, obj) {
        obj = obj['owner'];
        var total = 0;
        if (obj.hasOwnProperty('Modpacks')) {
            $.each(obj['Modpacks'], function (id, dl) {
                total += dl;
            })
        }
        table.addRow([name, total]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#modpack-owned')[0]).draw(table, {title: 'Modpack Downloads (Owner only)'});

    table = new google.visualization.DataTable();
    table.addColumn('string', 'Username');
    table.addColumn('number', 'Downloads');
    $.each(DATA['authors'], function (name, obj) {
        obj = obj['member'];
        var total = 0;
        if (obj.hasOwnProperty('Modpacks')) {
            $.each(obj['Modpacks'], function (id, dl) {
                total += dl;
            })
        }
        table.addRow([name, total]);
    });
    table.sort({column: 1, desc: true});
    new google.visualization.PieChart($('#modpack-member')[0]).draw(table, {title: 'Modpack Downloads (All members)'});
}

google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(function () {
    isLoadedCharts = true;
    if (isLoadedData) {
        run()
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
            run()
        }
    }
});
