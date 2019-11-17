if ($('#index').length > 0) {
    var ws = 70;
    var ls = 25;
    var gs = 360 - ws - (2 * ls);
    var rot = 90;
    var h1 = 200;
    var w1 = 200;
    var h2 = 160;
    var w2 = 160;
    var sz = 25;

    // TEMP
    var level = document.getElementById('temp').attributes.val.value;
    var gmin = 0;
    var gmax = 110;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_temp = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', '', '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#f44298',
                    '#f44741',
                    '#f48541',
                    '#f4af41',
                    '#edde42',
                    '#d6ed42',
                    '#78ed42',
                    '#42edae',
                    '#42d0ed',
                    '#4283ed',
                    '#424ded',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_temp = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h1,
        width: w1,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // DEWPT
    var level = document.getElementById('dewpt').attributes.val.value;
    var gmin = 0;
    var gmax = 110;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_dewpt = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, gs / 11, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', '', '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#f44298',
                    '#f44741',
                    '#f48541',
                    '#f4af41',
                    '#edde42',
                    '#d6ed42',
                    '#78ed42',
                    '#42edae',
                    '#42d0ed',
                    '#4283ed',
                    '#424ded',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_dewpt = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h1,
        width: w1,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // HUM
    var level = document.getElementById('hum').attributes.val.value;
    var gmin = 0;
    var gmax = 100;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_hum = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 5, gs / 5, gs / 5, gs / 5, gs / 5, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#4286f4',
                    '#41b8f4',
                    '#41f1f4',
                    '#41f455',
                    '#a9f441',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_hum = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h1,
        width: w1,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // PRES
    var level = document.getElementById('pres').attributes.val.value;
    var gmin = 29.7;
    var gmax = 30.5;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_pres = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 5, gs / 5, gs / 5, gs / 5, gs / 5, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#78ed42',
                    '#d6ed42',
                    '#edde42',
                    '#f4af41',
                    '#f48541',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_pres = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h1,
        width: w1,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // WINDDEG
    var level = document.getElementById('winddeg').attributes.val.value;
    var gmin = 0;
    var gmax = 360;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 + 90 - ((level - gmin) / (gmax - gmin) * 360),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_winddeg = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5, 22.5],
            hoverinfo: 'none',
            rotation: -11.25,
            sort: false,
            text: ['N', 'NNW', 'NW', 'WNW', 'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE', 'E', 'ENE', 'NE', 'NNE'],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    '#f45f42',
                    '#f7856f',
                    '#e2aba1',
                    '#d8bdb8',
                    '#BCBCBC',
                    '#bac8e0',
                    '#aeccfc',
                    '#77aaf9',
                    '#4186f4',
                    '#77aaf9',
                    '#aeccfc',
                    '#bac8e0',
                    '#BCBCBC',
                    '#d8bdb8',
                    '#e2aba1',
                    '#f7856f'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_winddeg = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h2,
        width: w2,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // WINDSPD
    var level = document.getElementById('wind').attributes.val1.value;
    var level2 = document.getElementById('wind').attributes.val2.value;
    var gmin = 0;
    var gmax = 15;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    if (level2 > gmax) {
        level2 = gmax;
    }
    if (level2 < gmin) {
        level2 = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var degrees = 360 - rot - ((level2 - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path3 = mainPath.concat(pathX, space, pathY, pathEnd);
    var path4 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_windspd = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, 80, 80, 48, 16, 12, 4, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', '', gmin.toString(), ''],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#ffff00',
                    '#ffcc00',
                    '#bfff00',
                    '#00cc00',
                    '#009999',
                    '#3366ff',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_windspd = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path3,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path4,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h2,
        width: w2,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // RAIN
    var level = document.getElementById('rain').attributes.val.value;
    var gmin = 0;
    var gmax = 1.0;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_rain = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 5, gs / 5, gs / 5, gs / 5, gs / 5, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#4286f4',
                    '#6399f2',
                    '#41b8f4',
                    '#41f1f4',
                    '#bcf6ff',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_rain = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h2,
        width: w2,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // SOLAR
    var level = document.getElementById('solar').attributes.val.value;
    var gmin = 0;
    var gmax = 1000;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_solar = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 5, gs / 5, gs / 5, gs / 5, gs / 5, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#ff9900',
                    '#ffb444',
                    '#ffd944',
                    '#fce58a',
                    '#fffcbc',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_solar = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h2,
        width: w2,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    // UV
    var level = document.getElementById('uv').attributes.val.value;
    var gmin = 0;
    var gmax = 8;
    var leveldisp = level;
    if (level > gmax) {
        level = gmax;
    }
    if (level < gmin) {
        level = gmin;
    }
    var degrees = 360 - rot - ((level - gmin) / (gmax - gmin) * gs),
        radius = 0.75;
    var radians = degrees * Math.PI / 180;
    var x = radius * Math.cos(radians);
    var y = radius * Math.sin(radians);
    var mainPath = 'M -.0 -0.075 L .0 0.075 L ',
        mainPath2 = 'M -0.075 -0 L .075 0 L ',
        pathX = String(x),
        space = ' ',
        pathY = String(y),
        pathEnd = ' Z';
    var path = mainPath.concat(pathX, space, pathY, pathEnd);
    var path2 = mainPath2.concat(pathX, space, pathY, pathEnd);

    var data_uv = [{
            type: 'scatter',
            x: [0],
            y: [0],
            marker: {
                size: sz,
                color: '#000000'
            },
            showlegend: false,
            hoverinfo: 'none'
        },
        {
            values: [ls, gs / 5, gs / 5, gs / 5, gs / 5, gs / 5, ls, ws],
            hoverinfo: 'none',
            rotation: rot - 30,
            sort: false,
            text: [gmax.toString(), '', '', '', '', '', gmin.toString(), leveldisp.toString()],
            textinfo: 'text',
            textposition: 'inside',
            marker: {
                colors: [
                    'rgba(110, 154, 22, 0)',
                    '#ff9990',
                    '#fcbbb5',
                    '#fcd1b5',
                    '#efd5c4',
                    '#f2e7e1',
                    'rgba(110, 154, 22, 0)', 'rgba(110, 154, 22, 0)'
                ]
            },
            hole: 0.5,
            type: 'pie',
            showlegend: false
        }
    ];

    var layout_uv = {
        shapes: [{
                type: 'path',
                path: path,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            },
            {
                type: 'path',
                path: path2,
                fillcolor: '#000000',
                line: {
                    color: '#000000'
                }
            }
        ],
        height: h2,
        width: w2,
        margin: {
            l: 0,
            r: 0,
            b: 0,
            t: 0,
            pad: 0
        },
        xaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        },
        yaxis: {
            zeroline: false,
            showticklabels: false,
            showgrid: false,
            range: [-1, 1],
            fixedrange: true
        }
    };

    Plotly.newPlot('gauge_temp', data_temp, layout_temp, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_dewpt', data_dewpt, layout_dewpt, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_hum', data_hum, layout_hum, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_pres', data_pres, layout_pres, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_winddeg', data_winddeg, layout_winddeg, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_windspd', data_windspd, layout_windspd, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_rain', data_rain, layout_rain, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_solar', data_solar, layout_solar, {
        displayModeBar: false
    });
    Plotly.newPlot('gauge_uv', data_uv, layout_uv, {
        displayModeBar: false
    });
}