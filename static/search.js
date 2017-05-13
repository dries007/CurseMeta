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

var currentList = 'mods';
var list_urls = {
    mods: URL_BASE + "mods.json",
    modpacks: URL_BASE + "modpacks.json"
};
var index = {};

var _getData_cache = {};
/**
 * Get data, cached or ajax
 * @param url Last part of URL, without extension json.
 * @param callback Callback
 */
function getData(url, callback) {
    if (_getData_cache.hasOwnProperty(url)) {
        callback(_getData_cache[url]);
    } else {
        $.getJSON(URL_BASE + url + ".json", function (data) {
            _getData_cache[url] = data;
            callback(data);
        });
    }
}

// For ability to cross-list depend jump, we need all ids mapped to what list they are from
getData("index", function (data) {
    $('#timestamp').text(data["timestamp_human"]);
    index = data;
});

/**
 * Formatting loop
 * @param data Data object
 * @param name Key that is an array in data
 * @param f Callback
 * @returns {string} Accumulative returns of callback
 */
function loop(data, name, f) {
    if (!data.hasOwnProperty(name)) return '';
    var out = '';
    $.each(data[name], function (i) {
        var r = f(data[name][i]);
        if ((typeof r) !== 'undefined') out += r;
    });
    return out;
}

/**
 * Called after row is added to DOM, so the jQ selectors work (also, it's async)
 * @param row
 */
function fixDownloadLinks(row) {
    var row_data = row.data();
    var child_node = row.child();
    child_node.find(".file").each(function(i, e) {
        var jQe = $(e);
        var download = jQe.find(".download");
        var dependencies = jQe.find(".dependencies");
        console.log(download);
        console.log(dependencies);
        getData(row_data["Id"] + '/' + jQe.data('fileid'), function (data) {
            download.replaceWith('<a href="' + data["DownloadURL"] + '" target="_blank">Download</a>');
            dependencies.replaceWith(makedeps(data));
        })
    });
}

/**
 * Truncate (and wrap in span with title)
 * @param str
 * @param len
 * @returns {*}
 */
function truncate(str, len) {
    if (str.length < len) return str;
    return '<span title="' + str + '">' + str.substr(0, len) + '&hellip;</span>';
}

function makedeps(obj) {
    var out = loop(obj, "Dependencies", function (dep) {
        var target = '#';
        var pid = parseInt(dep["AddOnId"]);
        $.each(list_urls, function (key) {
           if (index.hasOwnProperty(key) && index[key].indexOf(pid) !== -1) {
               target = '#' + key + '-' + pid;
           }
        });
        return '<a href="' + target + '" title="' + dep["Type"] + '">' + dep["AddOnId"] + '</a>&nbsp;'
    });
    return out === '' ? 'None' : out;
}

/**
 * Format files table
 * @returns {string} HTML
 */
function formatFileTable(data, rootId, idId, fileTypeId, nameId, urlID, gameVersionId) {
    return '<table>' +
        '<tr><th>MC</th><th>Id</th><th>Type</th><th>Filename</th><th>Download</th><th>Dependencies</th><th>JSON</th></tr>' +
        loop(data, rootId, function (obj) {
            var def = data["DefaultFileId"] === obj[idId];
            return '<tr '+ (def ? 'class="file default-file" title="Default file"' : 'class="file"' ) + ' data-fileid="' + obj[idId] + '"><td>' + [
                    obj[gameVersionId],
                    obj[idId],
                    obj[fileTypeId],
                    truncate(obj[nameId], 25),
                    urlID === null ? '<span class="download">Getting URL...</span>' : '<a href="' + obj[urlID] + '" target="_blank">Download</a>',
                    urlID === null ? '<span class="dependencies">Loading...</span>' : makedeps(obj),
                    '<a href="' + URL_BASE + data["Id"] + '/' + obj[idId] + '.json" target="_blank">JSON</a>'
                ].join('</td><td>') + '</td></tr>';
            }) +
        '</table>';
}

/**
 * Make child HTML
 * @param data Project Data object
 * @returns {string}
 */
function makeChildHTML(data) {
    // Only default image, skip the rest
    var image = loop(data, "Attachments", function (obj) {
        if (obj['IsDefault']) {
            return '<a href="' + obj['Url'] + '" target="_blank"><img class="logo" src="' + obj['ThumbnailUrl'] + '" title="' + $(obj['Description']).text() + '"></a>'
        }
    });

    // All authors
    var authors = '<ul>' + loop(data, "Authors", function (obj) {
        return '<li>' + obj["Name"] + '</li>';
    }) + '</ul>';

    // Link to Curse Project page
    var curseLink = '<p><a href="' + data["WebSiteURL"] + '" target="_blank"><b>Curse Project Page</b></a></p>';

    // Links to Curse and {project.json, project/index.json, project/files.json} from CurseMeta
    var links = '<ul><li>' + [
            '<a href="' + URL_BASE + data["Id"] + '.json" target="_blank">Project JSON</a>',
            '<a href="' + URL_BASE + data["Id"] + '/" target="_blank">Files ID list</a>',
            '<a href="' + URL_BASE + data["Id"] + '/files.json" target="_blank">Files JSON</a>'
        ].join('</li><li>') +
        '</li></ul>';

    // no code duplication yey
    // Also, yes "GameVesion" is misspelled. That's Curse's fault.
    var version_files = formatFileTable(data, "GameVersionLatestFiles", "ProjectFileID", "FileType", "ProjectFileName", null, "GameVesion");
    var latest_files = formatFileTable(data, "LatestFiles", "Id", "ReleaseType", "FileName", "DownloadURL", "GameVersion");

    // HTML
    return '<div class="info">' +
        '<div><h2>Info</h2>' + image + curseLink + '<h3>Authors</h3>' + authors + '<h3>CurseMeta Links</h3>' + links + '</div>' +
        '<div><h2>Latest Files per MC Version</h2>' + version_files + '</div>' +
        '<div><h2>Latest Files</h2>' + latest_files + '</div>' +
        '</div>'
}

/**
 * ON READY
 */
$(function () {
    // radio buttons
    $.each(list_urls, function (key, val) {
        $('#list-' + key).click(function () {
            //todo: something with state & history
            window.location.hash = '#' + key;
            table.ajax.url(val).load();
        })
    });

    var _prev_child = null;
    /**
     * Toggle child of row & scroll to it.
     * @param row Datatables row obj
     * @param forceShow {boolean} if true, ignore status and always show & scroll
     */
    function toggleChild(row, forceShow) {
        if (row.child.isShown() && !forceShow) {
            _prev_child = null;
            row.child.hide();
            $(row.node()).removeClass('shown');
        }
        else {
            if (_prev_child !== null) {
                _prev_child.child.hide();
                $(_prev_child.node()).removeClass('shown');
            }
            getData(row.data()['Id'], function (data) {
                row.child(makeChildHTML(data)).show();
                row.scrollTo(true);
                _prev_child = row;
                fixDownloadLinks(row);
            });
            $(row.node()).addClass('shown');
        }
    }

    // table is used in navigate, which is used before the var is made, and we'd like it to be null instead of undefined.
    var table = null;

    /**
     * Used to select the right list (and entry if required)
     * @param target
     */
    function navigate(target) {
        //todo: something with state & history
        // split = list-projectid
        target = target.split('-');
        if (!list_urls.hasOwnProperty(target[0])) {
            return navigate(currentList);
        }
        currentList = target[0];
        $('#list-' + target[0]).prop("checked", true);
        if (target.length > 1 && table !== null) {
            var row = table.row("#pid" + target[1]);
            toggleChild(row, true);
        }
        return list_urls[target[0]];
    }

    window.onpopstate = function(event) {
        navigate(window.location.hash ? window.location.hash.substr(1) : currentList);
    };

    // do the magic
    table = $('#table').DataTable({
        ajax: {
            // get proper URL, so we don't have to load this twice at the start
            url: navigate(window.location.hash ? window.location.hash.substr(1) : currentList),
            // insert ID and HTMLid into the data objects
            dataSrc: function (json) {
                var out = [];
                $.each(json, function (k, v) {
                    var row = $.extend({"Id": k, "HTMLid": "pid" + k}, v);
                    out.push(row);
                });
                return out;
            }
        },
        // select HTMLid as row id, cause it gets prepended with pid (projectId)
        rowId: 'HTMLid',
        columns: [
            { // icons set via CSS, no data
                "className": 'details-control',
                "orderable": false,
                "data": null,
                "defaultContent": ''
            },
            {"data": "Id"},
            {"data": "Name"},
            {"data": "PrimaryAuthorName"},
            {"data": "Summary"}
        ],
        order: [[ 1, "desc" ]],
        scrollY: "calc(100vh - 200px)", // magic numbers!
        deferRender: true, // keep elements off screen out of mem if possible
        scroller: true, // no pages for me sir
        stateSave: true, // save state to HTML session stuff. We use hash/history, but this also preserves search
        initComplete: function () { // re-navigate, so we scroll and unfold child
            navigate(window.location.hash ? window.location.hash.substr(1) : currentList);
        }
    });

    // (un)fold children on click
    $('#table tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);
        //todo: something with state & history
        window.location.hash = '#' + currentList + '-' + row.data()["Id"];
        toggleChild(row);
    });
});
