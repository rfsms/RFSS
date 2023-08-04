var lastb = 0;
var _p1 = 0;
var lastRIT = 0;
var satStat = {};
var ipan = 0;
var wkey = 0;
var lastW = 0;
var lastLookupTime;
var lastbs;
var qs = 0;
var hs = 0;
var doLookup = 0;
var lastqrz;
var storage;
var azmapoffset = 0.0;
var groundoffset = 0;
var capturemouse = 0;
var poppedElementName = 0;
var jsonreport = 0;
var pauseUpdates = '';
var drawMap = 2;
var lastSat = 0;
var green = 0;
var lat;
var lon;
var hlat;
var hlon;
var ldata;
var cdata;
var pathid = 0;
var groundTrack = 0;
var qsolog = 0;
var satPath = 0;
var globalssid = 0;
var groundTrackTime = 0;
var groundTrackRandom = Math.random();
var minEl = 5.0;
var degtorad = 3.14159 / 180.0;
var radtodeg = 180.0 / 3.14159;
var continuous = false
var predictList = 0;
var lastPredict = 0;
var satList = 0;
var freqRows = 17;
var btn;
var date;
var freqList = 0
var audiocontext;
var oscillator;
var fwWarning = `PLEASE REVIEW THE CHANGELOG FOR IMPORTANT INFORMATION BEFORE PERFOMRING A FIRMWARE UPDATE\n\nA reliable internet connection and power supply is required for a firmware update.\nAn interruption during downloading or a malfunction may cause corruption in the firmware and your equipment may stop functioning normally. \nDo not remove power from the equipment during the update.If such a failure of the firmware results in your equipment not functioning normally, CSN Technologies. expressly denies and is free from any and all responsibility arising from the result of damage from such an event.\n\nI fully understand the above, and agree not to hold CSN Technologies responsible for any damage to my equipment operation or loss of data as a result of this download. \n\nClick Continue to check and update the equipment to the latest firmware or Cancel to abort the update.`;
var noLCDBr = 'X';
var dbg = 1;
var beep = new Audio("data:audio/mpeg;base64,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");
var clearmsg = 0;
var sub = 0;
var subchk = 1;
var suben = 0;
var strk = 1;
var gsats;
var gsatsD = 0;
var savex = 0;

function _z2(e) {
    if (!capturemouse) return;
    var c = _d('cTrack2');
    var rect = c.getBoundingClientRect();
    x = (e.clientX - rect.left) / (rect.left - rect.width) * c.width;
    var dx = Math.abs(x - savex);
    if (dx < 2) return;
    var center_h = c.height / 2;
    var inc = 1.0;
    if (((e.clientY - rect.top) / (rect.bottom - rect.top) * c.height) > center_h) {
        inc = -inc;
    }
    if (x > savex) azmapoffset += inc;
    else azmapoffset -= inc;
    savex = x
    storage.setItem("azmapoffset", azmapoffset);
    _l1(ldata);
}

function Mob() {
    return ((window.innerWidth < 960) || (window.innerHeight <= 600));
}
/*
function radc() {if(_d('radtype').value=='8') {_d('rrigip').style.display='inline';
_d('rradb').style.display='none';
}
else {_d('rrigip').style.display='none';
_d('rradb').style.display='block';
}}
*/
var dnxt = 0;

function _y2(f = -1) {
    if (f > -1) dnxt = f;
    else dnxt = !dnxt;
    dx = _d('divnxt');
    dy = _d('nxtc');
    ds = _d('divsky3');
    console.log(window.innerWidth, Mob());
    if (dnxt) {
        h = ds.clientHeight;
        ds.style.display = 'none';
        dx.style.display = 'block';
        if (Mob()) {
            dx.clientHeight = '4000px'
            dx.style.maxHeight = 'none';
        } else {
            console.log('correct', h);
            dx.clientHeight = h + 'px';
            dx.style.maxHeight = h + 'px';
            dy.style.maxHeight = parseInt(h * 0.90) + 'px';
        }
    } else {
        dx.style.display = 'none';
        ds.style.display = 'block';
    }
}

function uppre() {
    p = _d('nxt');
    s = '';
    if (!predictList) {
        p.innerHTML = '';
        return;
    }
    n = new Date().getTime() / 1000;
    n = ldata.time;
    m = parseFloat(_d('minpass').value);
    s += 'SATELLITE'.padEnd(16);
    s += 'MAX EL'.padStart(7).padEnd(9);
    s += 'AOS'.padEnd(14);
    s += 'TTGO\n';
    cnt = 0;
    predictList.list.forEach(x => {
        if (x[0]) {
            if (cnt++ > 50) return;
            if (x[7] > m && x[3] > n) {
                c = (n > x[2] && n < x[3]) ? 'lime' : 'white';
                s += `<span style='font-size:1em;color:${c};cursor:pointer' onclick='_d4("${x[1]}","${x[9]}")'>` + x[1].substring(0, 14).padEnd(16) + '</span>';
                t = x[7].toString().padStart(7);
                s += t.padEnd(9);
                s += _r1(x[2]).padEnd(14);
                t = x[2] - n;
                if (t > 0) s += toHHMMSS(t).padEnd(7);
                else s += toHHMMSS(x[3] - n).padEnd(7);
                s += "\n";
            }
        }
    });
    p.innerHTML = s;
}

function apan(c) {
    ipan = 1;
    _f1("Z|n|" + c)
    window.event.preventDefault();
}

function rch(e) {
    d = parseInt(_d('fdwnr').value * 1000);
    if (d == 0) e.checked = false;
}

function bkset() {
    window.open('/set');
}

function _w2() {
    window.open('/set');
}

function dfreq() {
    window.open('/f.txt');
}

function _x2() {
    if (confirm("Are you sure you want to factory reset the frequency database?")) _f1("Z|h|");
}

function _v2(e) {
    if (!capturemouse) return;
    var c = _d('cTrack3');
    var rect = c.getBoundingClientRect();
    x = (e.clientX - rect.left) / (rect.left - rect.width) * c.width;
    var dx = Math.abs(x - savex);
    if (dx < 2) return;
    if (x > savex) groundoffset -= 1.2;
    else groundoffset += 1.2;
    savex = x;
    _m1(ldata);
}

function _d(e) {
    return document.getElementById(e);
}

function pop(ename) {
    if (poppedElementName) hide(poppedElementName);
    poppedElementName = ename;
    var vw = window.innerWidth;
    var e = _d(ename);
    if (vw < 960) {
        e.style.left = '0px';
        e.style.width = '100%';
    }
    e.style.top = window.scrollY + 30 + 'px';
    e.style.display = 'block';
    var m = _d('blackimg');
    m.style.display = 'block';
    m.style.position = 'absolute';
    m.style.left = 0;
    m.style.top = 0;
    m.style.zIndex = 2;
    m.style.opacity = 0.65;
    m.style.width = document.documentElement.clientWidth + 'px';
    m.style.height = (document.documentElement.clientHeight + vw) + 'px';
    if (ename == 'divcontrol') _g3(1);
    if (ename == 'divlog') {
        lastLookupTime = 0;
        _d('logCallsign').focus();
        if (qs == 0) h1_(0);
    }
    if (ename == 'divlocation') {
        qs = 0;
        hs = 0;
        _d('qrzp').type = 'password';
    }
}

function hide(ename) {
    _d(ename).style.display = 'none';
    _d('blackimg').style.zIndex = -100;
    _d('blackimg').style.display = 'none';
    poppedElementName = 0;
    if (ename == 'divlocation') {
        _d('qrzp').type = 'text';
    }
}

function _u2() {
    if (poppedElementName) hide(poppedElementName);
}

function _j2() {
    _g1(true);
}

function _i2() {
    if (pauseUpdates.length > 0) {
        console.log('Updates paused-' + pauseUpdates);
        setTimeout(_i2, 500);
    } else {
        _g1(false);
        setTimeout(_i2, 2750);
    }
}

function _k2() {
    if (ldata.gpsen) {
        if (!ldata.gpslock) {
            alert('No GPS Lock');
            return;
        }
        _d('lat').value = ldata.gpslat;
        _d('lon').value = ldata.gpslon;
        _d('grid').value = ldata.gpsgr;
    }
}

function _l2() {
    window.open("/adif");
}

function _m2() {
    _d('logmessage').innerHTML = '';
    _f1('B|LD||||');
    setTimeout(function() {
        getSched(0);
    }, 300);
}

function _n2() {
    _d('logmessage').innerHTML = '';
    _f1('B|SV||||');
    setTimeout(function() {
        getSched(0);
    }, 300);
}

function _o2() {
    _d('logmessage').innerHTML = '';
    if (confirm("Are you sure you want clear the entire schedule?")) {
        _f1('B|C||||');
        setTimeout(function() {
            getSched(0);
        }, 300);
    }
}

function _p2() {
    _d('logmessage').innerHTML = '';
    if (confirm("Are you sure you want clear the entire QSO log?")) {
        _f1('Q|!@||||');
        setTimeout(function() {
            qsolog = 0
        }, 300);
    }
}

function _q2(idx) {
    _d('logmessage').innerHTML = '';
    if (confirm("Are you sure you want remove this log entry?")) {
        _f1('Q|!d|' + idx + '|||');
        setTimeout(function() {
            qsolog = 0
        }, 300);
    }
}

function _r2(idx) {
    _d('logmessage').innerHTML = '';
    if (confirm("Are you sure you want remove this entry?")) {
        _f1('B|DE|' + idx + '|||');
        setTimeout(function() {
            getSched(0);
        }, 300);
    }
}

function _s2() {
    _d('logCallsign').value = '';
    _d('logGridsquare').value = '';
    _d('logst').value = '';
    _d('logcntry').value = '';
    _d('logCallname').value = '';
    _d('logRSTSent').value = '59';
    _d('logRSTRecv').value = '59';
    _d('logCallsign').focus();
    _d('logmessage').innerHTML = '';
}

function _t2() {
    _d('logmessage').innerHTML = '';
    let call = _d('logCallsign').value.trim().toUpperCase();
    if (call.length < 1) {
        alert("Callsign cannot be blank");
        return;
    }
    // _f1('Q|'+ call +'|'+ _d('logGridsquare').value +'|'+_d('logRSTSent').value+'|'+_d('logRSTRecv').value+'|'+ _d('logComment').value+'|'+ _d('logCallname').value )
    var c = _d('logComment').value;
    if (c.indexOf("$c") >= 0) {
        c = c.replace("$c", call);
    }
    if (c.indexOf("$m") >= 0) {
        c = c.replace("$m", _d('call').value);
    }
    if (c.indexOf("$n") >= 0) {
        c = c.replace("$n", _d('logCallname').value);
    }
    if (c.indexOf("$s") >= 0) {
        c = c.replace("$s", _d('searchname').value);
    }
    var s = call +
        '^' + _d('logGridsquare').value +
        '^' + _d('logRSTSent').value +
        '^' + _d('logRSTRecv').value +
        '^' + c +
        '^' + _d('logCallname').value +
        '^' + _d('logst').value.toUpperCase() +
        '^' + _d('logcntry').value +
        '^' + lastLookupTime.toFixed(0);
    _f1('Q|' + s)
    setTimeout(function() {
        qsolog = 0
    }, 500);
    _d('logCallsign').value = '';
    _d('logGridsquare').value = '';
    _d('logCallname').value = '';
    _d('logst').value = '';
    _d('logcntry').value = '';
    _d('logRSTSent').value = '59';
    _d('logRSTRecv').value = '59';
    _d('logCallsign').focus();
}

function onDocReady() {
    date = new Date();
    let objNode = ce("div");
    objNode.style.width = "100vw";
    document.body.appendChild(objNode);
    let intViewportWidth = objNode.offsetWidth;
    document.body.removeChild(objNode);
    if (intViewportWidth < 960) {
        let c = _d('charts');
        let r = _d('chartsifnarrow');
        document.body.insertBefore(c, r);
    }
    if (_e1()) {
        console.log("On iPad,iPhone");
        var el = document.getElementsByTagName('select');
        for (var i = 0; i < el.length; i++) {
            if (el[i]) {
                el[i].classList.remove("t-bl");
                el[i].style.backgroundColor = '#FFFFFF';
                el[i].style.color = '#000000';
            }
        }
        var el = document.getElementsByTagName('input');
        for (var i = 0; i < el.length; i++) {
            if (el[i] && el[i].type == 'button') {
                el[i].classList.remove("t-bl");
                el[i].style.backgroundColor = '#7777CC';
                el[i].style.color = '#000000';
            }
        }
    }
    _d('sstat').value = -1;
    document.addEventListener("keypress", keypr);
    _q();
    _b2();
    storage = window.localStorage;
    suben = storage.getItem("suben");
    if (suben == null) suben = '1';
    suben = parseInt(suben);
    _d('sub').value = suben;
    setTimeout(_d3, 200);
    setTimeout(_j2, 750);
    setTimeout(_i2, 2000);
    aebut();
    setTimeout(_h4Loop, 500);
    window.addEventListener("message", function(event) {
        _z(event.data);
    });
    azmapoffset = parseFloat(storage.getItem("azmapoffset"));
    if (!azmapoffset) azmapoffset = 0;
    _d('logComment').value = storage.getItem('lc');
    _e4(false);
}

function _h2() {
    beep.currentTime = 0;
    beep.play();
}

function Beep(c) {
    setTimeout(function() {
        _h2();
    }, 0);
    c--;
    for (var i = 1; i <= c; i++) {
        setTimeout(function() {
            _h2();
        }, 400 * i);
    }
}

function cmpf2(a, b) {
    return b.sort - a.sort;
}

function cmpf(a, b) {
    return (b.flags & 4) - (a.flags & 4);
}

function _z1(data) {
    if (data.satname) {
        if (document.activeElement.id != 'searchname') {
            _d('searchname').value = data.satname;
        }
        if (lastSat != data.satname) {
            groundTrack = 0;
            satPath = 0;
        }
        lastSat = data.satname;
    }
    ar = '';
    if (data.satAZ && data.satEL) {
        if (ldata) {
            if (data.sdel == 1) ar = '&darr;';
            else ar = '&uarr;';
        }
        ecl = '&#9788;';
        if (data.satecl == 1) ecl = '&#9790;';
        _d('satpos').innerHTML = `AZ: ${data.satAZ.toFixed(1)}&deg; / EL: ${data.satEL.toFixed(1)}&deg;` + ar + ecl;
    } else _d('satpos').innerHTML = '';
    _d('satnoglink').href = `https://db.satnogs.org/satellite/${data.catno}#mapcontent`;
    _d('otracklink').href = `https://www.orbtrack.org/#/?satSCN=${data.catno}`;
    if (data.rng) {
        _d('rng').innerHTML = data.rng.toFixed(1) + ' Km / ' + (data.rng * 0.621371).toFixed(1) + ' Mi';
    } else _d('rng').innerHTML = '';
    try {
        if (pathid != data.pathid) {
            satPath = 0;
            groundTrack = 0;
            _d('sstat').value = -1;
            _q();
        }
        pathid = data.pathid;
    } catch (err) {
        if (dbg) console.log(err);
    }
    if (data.aosAZ && data.aosTime) {
        var s = _r1(data.aosTime) + ' @ ' + data.aosAZ.toFixed(1) + '&deg;';
        if (data.ttaos > 1) {
            s = s + " (TTGO " + toHHMMSS(data.ttaos - 2) + ")";
        }
        _d('aos').innerHTML = s;
    } else _d('aos').innerHTML = '';
    if (data.losAZ && data.losTime) {
        var s = _r1(data.losTime) + ' @ ' + data.losAZ.toFixed(1) + '&deg;';
        if (data.ttlos > 1) {
            s = s + " (TTGO " + toHHMMSS(data.ttlos - 2) + ")";
        }
        _d('los').innerHTML = s;
    } else _d('los').innerHTML = '';
    if (data.maxEL) _d('maxel').innerHTML = data.maxEL.toFixed(1) + '&deg;';
    _t1(_d('bSDR'), data.sdrc, 'SDR D/L')
    try {
        var fc = 1;
        data.freq.sort(cmpf);
        data.freq.sort(cmpf2);
        for (pt of data.freq) {
            _d('freqrow' + fc).style.display = 'block';
            if (pt.sort == 1) _d('freqrow' + fc).style.color = '#d0ebff';
            else _d('freqrow' + fc).style.color = '#77AAFF';
            _d('raddescr' + fc).innerHTML = pt.descr;
            _d('raddescr' + fc).value = pt.uid;
            let a = 0;
            if (data.afreq == pt.uid) a = 1;
            rit = '';
            if (parseInt(pt.fdwnr) != 0) {
                col = (pt.flags & 2) ? 'lime' : 'gray';
                rit = '<sup class="text-' + col + '" style="font-size:0.6em">(' + (parseInt(pt.fdwnr) / 1000).toFixed(3) + ')</sup>';
            }
            _d('radup' + fc).innerHTML = '<span title="Click To Edit" class="hand t-bl" onclick="_y1(' + pt.id + ')">' + (pt.upFreq / 1000000.0).toFixed(3) + '</span>';
            _d('raddown' + fc).innerHTML = '<span title="Click To Edit" class="hand t-bl" onclick="_y1(' + pt.id + ')">' + (pt.downFreq / 1000000.0).toFixed(3) + rit + '</span>';
            if (a) {
                var u = (pt.upFreq / 1000000.0).toFixed(3);
                var d = (pt.downFreq / 1000000.0).toFixed(3);
                var ud = pt.dop_up.toFixed(0);
                var dd = pt.dop_down.toFixed(0);
                var ru = ((pt.upFreq + pt.dop_up + pt.off_up) / 1000000.0).toFixed(3);
                var rd = ((pt.downFreq + pt.dop_down + pt.off_down) / 1000000.0).toFixed(3);
                _d('freqrow' + fc).style.backgroundColor = '#004400';
                _d('freqactivename').innerHTML = `${pt.descr}`;
                _d('freqactivefreq').innerHTML = `${ru} / ${rd}`;
                _d('freqactivedop').innerHTML = `${ud}Hz / ${dd}Hz`;
                if (pt.fbw) {
                    umx = pt.downFreq + (pt.fbw * 1000) / 2;
                    umn = pt.downFreq - (pt.fbw * 1000) / 2;
                    cf = pt.downFreq + pt.off_down /*+pt.dop_down*/ ;
                    d = cf - umn;
                    px = (d / (umx - umn)) * 150;
                    if (px >= 150 || px <= 0) {
                        px = (px <= 0) ? 0 : 150;
                        _d('bwout').style.backgroundColor = 'red';
                        _d('bwin').style.backgroundColor = 'red';
                    } else {
                        _d('bwout').style.backgroundColor = '#acacac';
                        _d('bwin').style.backgroundColor = '#acacac';
                    }
                    _d('bwin').style.width = `${px}px`;
                    _d('txbw').innerHTML = `&plusmn;${pt.fbw/2}kHz`;
                } else _d('txbw').innerHTML = '';
            } else {
                _d('freqrow' + fc).style.backgroundColor = 'transparent';
            }
            fc++;
        }
    } catch (err) {
        if (dbg) console.log(err);
    }
}

function _f2() {
    var fup = parseFloat(_d('transup').value) * 1000000;
    if (!fup) fup = '0';
    var fdown = parseFloat(_d('transdown').value) * 1000000;
    if (!fdown) fdown = '0';
    var fname = _d('transname').value;
    if (!fname) fname = 'Manual Entry';
    _f1('b|' + (fup) + '|' + (fdown) + '|' + fname);
    hide("divaddtrans");
}

function _g2() {
    pe = _d('sps');
    pe2 = _d('sps2');
    p = pe.value.trim();
    p2 = pe2.value.trim();
    l = p.length;
    if (l > 2) {
        r = 0;
        pw = 'Password';
        if (l > 14) r = pw + ' too long';
        if (p != p2) r = pw + 's do not match';
        if (!p.match(/^[0-9a-zA-B]+$/)) r = pw + ' must be alphanumeric';
        if (r) {
            pe.value = '';
            pe2.value = '';
            pe.focus();
            alert(r);
            return;
        }
    }
    _p3();
    _t3();
    _e2();
    setTimeout(function() {
        _f1('Z|p|' + p);
        if (p.length) setTimeout(function() {
            window.location = '/';
        }, 1000)
    }, 2000);
    hide('divlocation');
}

function _e2() {
    _f1('Z|Q|' + _d('qty').value + '|' + _d('qip').value + '|' + _d('qpt').value + '|' + _d('qdxpt').value);
}

function _d2() {
    if (confirm('Are you sure?')) {
        _f1('R|X');
    }
}

function handleMin(m) {
    ldata.time = m.time;
    ldata.az = m.az;
    ldata.el = m.el;
    ldata.satAZ = m.satAZ;
    ldata.satEL = m.satEL;
    ldata.satLat = m.satLat;
    ldata.satLon = m.satLon;
    _c2(ldata, 0);
    u = (m.upFreq / 1000000.0).toFixed(3);
    d = (m.downFreq / 1000000.0).toFixed(3);
    ud = m.dop_up.toFixed(0);
    dd = m.dop_down.toFixed(0);
    ru = ((m.upFreq + m.dop_up + m.off_up) / 1000000.0).toFixed(3);
    rd = ((m.downFreq + m.dop_down + m.off_down) / 1000000.0).toFixed(3);
    _d('freqactivefreq').innerHTML = `${ru} / ${rd}`;
    _d('freqactivedop').innerHTML = `${ud}Hz / ${dd}Hz`;
}

function _c2(data, manual) {
    if (manual) cdata = data;
    if (gsatsD) _f3(0);
    if (data.mode == 0) _d('sstat').value = -1;
    try {
        if ((ldata.mode == 1) && (data.mode == 0)) {
            _q();
        }
    } catch (e) {};
    if (clearmsg) {
        _d('message').innerHTML = '';
        clearmsg = false;
    }
    if (pauseUpdates.length > 0) {
        return;
    }
    windows.forEach(passData);
    _b2(data);
    if (subchk) {
        subchk = 0;
        setTimeout(_a4, 250);
    }
    try {
        _d('tme').innerHTML = _n1(data.time);
    } catch (e) {};
    try {
        uppre();
    } catch (e) {};
    if (manual) {
        _d('dver').innerHTML = data.dashver.toFixed(3);
        _d('fw').innerHTML = data.fw.toFixed(3);
        _d('serial').innerHTML = data.serial;
        if (noLCDBr.indexOf(data.serial) > 0) _d('lcdctl').style = 'display:none';
        _d('lat').value = data.lat.toFixed(6);
        _d('lon').value = data.lon.toFixed(6);
        lat = data.lat;
        lon = data.lon;
        hlat = data.lat;
        hlon = data.lon;
        _d('tzoffset').value = ((data.tz / 60) / 60).toString();
        _d('lcdunits').value = data.lcdunits;
        _d('timef').value = data.timef;
        _d('mac').value = data.mac;
        _d('toleranceAZ').value = data.toleranceAZ.toFixed(1);
        _d('tleurl').value = data.tleurl;
        _d('qrzl').value = data.qrzl;
        _d('qrzp').value = data.qrzp;
        _d('lcdbright').value = data.lcd;
        _d('gpsen').value = data.gpsen;
        _d('toleranceEL').value = data.toleranceEL.toFixed(1);
        _d('rotatorType').value = data.rotatorType;
        setTimeout(function() {
            _a2(0);
        }, 300);
        _d('minpass').value = data.mine;
        _d('rotip').value = data.rip;
        if (data.rigport > 0) {
            _d('bSDR').style.display = 'inline';
        } else {
            _d('bSDR').style.display = 'none';
        }
        /*
        _d('localip').value=data.localip;
        _d('gateway').value=data.gateway;
        _d('subnet').value=data.subnet;
        _d('primarydns').value=data.primarydns;
        _d('secondarydns').value=data.secondarydns;
        _d('ntpserver').value=data.ntpserver;
        */
        if (data.disableFlip == 1) _d('antflip').value = '0';
        else _d('antflip').value = '1';
        _d('psts').value = data.PSTS;
        /*_d('sps').value=atob(data.sp);
        _d('sps2').value=atob(data.sp);*/
        _d('parkAZ').value = data.parkAZ;
        _d('parkEL').value = data.parkEL;
        _d('readyAZ').value = data.readyAZ;
        _d('readyEL').value = data.readyEL;
        _d('postpass').value = data.postpass;
        _d('antqual').value = data.antq;
        _d('radtype').value = data.rigMod;
        _d('radbaud').value = data.rigBaud.toString();
        _d('radaddress').value = parseInt(data.rigAddress).toString(16) + 'h';
        _d('radvfo').value = data.rigVFO;
        _d('radinterval').value = data.rigInterval;
        _d('radminf').value = data.rigMinf;
        _d('radip').value = data.rigip;
        _d('radprt').value = data.rigport;
        _d('rap').value = data.rap;
        if (data.rapf < 100000000) _d('rapf').value = (data.rapf / 1000000).toFixed(0);
        else _d('rapf').value = (data.rapf / 1000000).toFixed(6);
        _d('rapm').value = data.rapm;
        _d('rapp').value = data.rapp;
        _d('ts').value = data.ts;
        _d('groundtrack').value = Math.abs(data.groundTrack);
        if (data.groundTrack < 0) _d('gtrktype').value = 1;
        else _d('gtrktype').value = 0;
        var select = _d("ssid");
        globalssid = data.ssid;
        _d('tledate').innerHTML = _n1(data.tledate);
        _d('autotle').value = data.autotle;
        if (data.call.length < 15) _d('call').value = data.call;
        if (data.grid.length < 7) _d('grid').value = data.grid;
        if (data.autotle > 0) {
            var autoUpdateTime = data.tledate + (data.autotle * 86400);
            _d('nexttledate').innerHTML = _n1(autoUpdateTime);
        } else {
            _d('nexttledate').innerHTML = "DISABLED";
        }
        if (data.aosbeepdeg) {
            _d('aosbeepdeg').value = _r(data.aosbeepdeg);
            _d('playalarm').value = data.playAlarm;
        }
        _d('qip').value = data.qip;
        _d('qpt').value = data.qpt;
        _d('qty').value = data.qty;
        _d('qdxpt').value = data.qdxpt;
        if (data.relay == 1) {
            _d('enRelay').value = 1;
        } else if (data.relay == -1) {
            _d('enRelay').value = 0;
        }
        _d('wkey').value = data.wkey;
    } else {
        if (data.mode == 1) {
            _z1(data);
        } else {
            _d('satpos').innerHTML = '--';
            _d('aos').innerHTML = '--';
            _d('los').innerHTML = '--';
            _d('rng').innerHTML = '--';
            _d('maxel').innerHTML = '--';
        }
    }
    if (!isNaN(data.az)) {
        _d('ant').innerHTML = `AZ: ${data.az.toFixed(1)}&deg; / EL: ${data.el.toFixed(1)}&deg;`;
        _d('ant2').innerHTML = `AZ: ${data.az.toFixed(0)}&deg; EL: ${data.el.toFixed(0)}&deg;`;
        _d('antvolts').innerHTML = `AZ: ${data.voltsAZ.toFixed(3)} / EL: ${data.voltsEL.toFixed(3)}`;
        if (data.flipped == 1) {
            _d('ant').innerHTML += ' (REVERSE)';
        } else {
            _d('ant').innerHTML += '';
        }
    } else {
        _d('ant').innerHTML = '';
    }
    gpsitems = document.querySelectorAll('.gpsitem');
    if (data.gpsav == 1) {
        e = _d('gpsstat');
        if (data.gpslock) {
            e.innerHTML = `${data.gpssats} SATS ${data.gpsgr}`;
            e.title = `${data.gpslat}, ${data.gpslon}`;
        } else {
            e.innerHTML = `NO LOCK: ${data.gpssats} SATS`;
            e.title = '';
        }
        if (data.gpslock && (data.gpsen >= 7)) {
            e.style = 'color:lime !important;';
            lat = data.gpslat;
            lon = data.gpslon;
        } else {
            e.style = 'color:#ff5a36 !important;';
            lat = _d('lat').value;
            lon = _d('lon').value;
        }
        gpsitems.forEach(function(e) {
            e.style = 'display:inline';
        });
    } else {
        gpsitems.forEach(function(e) {
            e.style = 'display:none';
        });
    }
    if (data.continuous == 1) continuous = true;
    else continuous = false;
    _t1(_d('btncontinue'), data.continuous, 'Continuous Mode')
    _t1(_d('bCW'), data.CW, 'Quick CW Mode')
    _t1(_d('btnschedule'), data.sched, 'Schedule');
    _d('modeA').value = data.mode_0;
    _d('modeB').value = data.mode_1;
    _d('PL').value = data.pl_0;
    if (data.power <= 100) {
        _d('pwr').innerHTML = data.power + '%';
        _d('power').value = data.power;
    }
    _d('TBW').value = data.tbw;
    _t1(_d('btnRig'), data.rigEnabled, 'Radio');
    _t1(_d('btnLockVFO'), data.lockVFO, 'Lock VFO');
    if (data.popup.length > 0) {
        data.msg = data.popup;
        if (data.msg.indexOf('sats loaded') > -1) setTimeout(_j2, 250);
        alert(data.popup);
    }
    if (data.msg.length > 0) {
        _d('message').innerHTML = data.msg.toUpperCase();
        _d('logmessage').innerHTML = data.msg.toUpperCase();
        if (data.msg.indexOf('WiFi Connected') >= 0) _d3();
        if (data.msg.indexOf('AOS ALARM') >= 0) {
            if (_d('playalarm').value >= 1) Beep(3);
        }
    }
    ldata = data;
    if (!qsolog) getLog();
    _b1();
}

function _x1(idx, updown, freq) {
    v = prompt('Enter new center frequency in MHz:', freq / 1000000.0);
    if (v) {
        v = parseFloat(v);
        v = v * 1000000;
        v = parseInt(v);
        _f1('C|' + idx + '|' + updown + '|' + v);
    }
}

function _y1(id) {
    if (id > -1) {
        ldata.freq.forEach(x => {
            if (x.id == id) {
                _d('dsc').value = x.descr.trim();
                _d('mup').value = x.upMode;
                _d('fup').value = (x.upFreq / 1000000).toFixed(6);
                _d('pup').value = x.plu;
                _d('fdwn').value = (x.downFreq / 1000000).toFixed(6);
                _d('mdwn').value = x.downMode;
                _d('fdwnr').value = (x.fdwnr / 1000.0).toFixed(3);
                if (x.fbw) _d('fbw').value = x.fbw;
                else _d('fbw').value = '';
                _d('fid').value = x.id;
                _d('fuid').value = x.uid;
                if (x.flags & 2) _d('rapl').checked = true;
                else _d('rapl').checked = false;
                _d('rdef').checked = (x.sort == 1);
            }
        });
    } else {
        _d('fuid').value = '0';
        _d('dsc').value = '';
        _d('mup').value = '';
        _d('fdwnr').value = '0';
        _d('fbw').value = '';
        _d('fup').value = '0';
        _d('pup').value = '';
        _d('fdwn').value = '0';
        _d('mdwn').value = '';
        _d('fid').value = '9999';
    }
    _d('sr').innerHTML = _d('searchname').value;
    pop('divtrans');
}

function savet() {
    err = 0;
    _d('dsc').value.replace(',', ' ');
    _d('mup').value = _d('mup').value.toUpperCase();
    _d('mdwn').value = _d('mdwn').value.toUpperCase();
    _d('dsc').value = _d('dsc').value.substring(0, 64);
    if (isNaN(parseFloat(_d('fup').value)) || isNaN(parseFloat(_d('fdwn').value))) err = 'Number required for frequency';
    if (isNaN(parseFloat(_d('fdwnr').value))) err += "\nNumber required for RIT";
    if (err) {
        alert(err);
        return;
    }
    if ((parseFloat(_d('fdwnr').value) > 9.999) || (parseFloat(_d('fdwnr').value) < -9.999)) {
        alert('RIT must be between -9.999 and 9.999');
        return;
    }
    if (!isNaN(_d('pup').value)) _d('pup').value = Math.floor(_d('pup').value);
    else _d('pup').value = '0';
    if (!isNaN(_d('fbw').value)) _d('fbw').value = Math.floor(_d('fbw').value);
    else _d('fbw').value = '0';
    let plu = parseInt(_d('pup').value) || 0;
    if (_d('rapl').checked) {
        plu += 900;
    }
    if (_d('rdef').checked) {
        if (!plu) plu = -1;
        else plu = -plu;
    }
    rec = _d('fid').value + '|' + _d('mup').value + '|' + (_d('fup').value * 1000000) + '|' + plu + '|' + (_d('fdwn').value * 1000000) + '|' + _d('mdwn').value + '|' + _d('dsc').value + '|' + _d('fdwnr').value + '|' + _d('fuid').value + '|' + _d('fbw').value;
    _f1('X|' + rec);
    _q();
    hide("divtrans");
}

function _b2(data) {
    if (!data) return;
    _l1(data);
    _m1(data, 0);
    _w1(data, 0);
}

function keypr(e) {
    if (e.key == 'Enter' && btn) {
        btn.click();
        e.preventDefault();
        return true;
    }
    switch (document.activeElement.tagName) {
        case 'INPUT':
        case 'BUTTON':
        case 'SELECT':
            return;
    }
    switch (e.key) {
        case 'Enter':
        case 'm':
        case 'M':
            _a3();
            break;
        case 's':
        case 'S':
            stop();
            break;
        case 'f':
        case 'F':
            _b4(true);
            break;
        case 'a':
        case 'A':
        case 'v':
        case 'V':
            _e4(1);
            break;
        case 'c':
        case 'C':
            _k3();
            break;
        case 'p':
        case 'P':
            _d("divcontrolvis").style.display = 'block';
            _d("az").focus();
            break;
        case 'r':
        case 'R':
            togglevisible("divradiovis");
            break;
        case 'Esc':
        case 'Escape':
            stop();
            break;
        default:
            return;
    }
    e.preventDefault();
    return true;
}

function clkm(e) {
    c = window.event;
    if ((c.clientX < e.offsetWidth - 30) || (c.clientY < e.offsetHeight - 30)) return;
    strk = !strk;
    _w1(ldata);
}

function _w1(data) {
    var c = _d('cTrack1');
    c.width = 600;
    c.height = 300;
    var ctx = c.getContext("2d");
    var w = c.width;
    var h = c.height;
    var img
    img = _d("mapimg");
    ctx.clearRect(0, 0, w, h);
    try {
        ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, c.width, c.height);
    } catch (e) {
        return;
    }
    if (!data) return;
    try {
        var px = _u1(hlon * degtorad);
        var py = _v1(hlat * degtorad);
        ctx.beginPath();
        ctx.lineWidth = 1;
        ctx.strokeStyle = "white"
        ctx.moveTo(px, py - 5);
        ctx.lineTo(px, py + 5);
        ctx.moveTo(px - 5, py);
        ctx.lineTo(px + 5, py);
        ctx.stroke();
    } catch (e) {
        return;
    }
    _s1(ctx, data);
    if (data.mode != 1) return;
    if (!groundTrack || (data.time - groundTrackTime > data.groundTrackTime * 59)) {
        getGroundTrack();
    }
    if (groundTrack && strk) {
        ctx.beginPath();
        ctx.strokeStyle = "cyan";
        var n = 0;
        for (pt of groundTrack.gtrack) {
            y = _v1(pt.Lat);
            x = _u1(pt.Lon);
            if (x < 0) x = 600 - x;
            if ((n++ == 0) || Math.abs(lastX - x) > 500) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
            lastX = x;
            lastY = y;
        }
        ctx.stroke();
        ctx.strokeStyle = "yellow";
        ctx.fillStyle = "magenta";
        ctx.font = "10px sans-serif"
        var n = 0;
        var lastt = 0;
        var elFlag = 0;
        for (pt of groundTrack.gtrack) {
            if (pt.time - lastt > (15 + (groundTrackRandom * 20)) * 60 || (pt.El > 0 && !elFlag)) {
                y = _v1(pt.Lat);
                x = _u1(pt.Lon);
                if (x < 0) x = 600 - x;
                dot(ctx, x, y, 1);
                ctx.fillStyle = "black";
                ctx.fillRect(x + 3, y - 4, ctx.measureText(pt.time).width + 2, 7);
                if (pt.El > 0) ctx.fillStyle = "magenta";
                else ctx.fillStyle = "cyan";
                ctx.fillText(_r1(pt.time), x + 3, y + 3);
                lastt = pt.time;
                if (!elFlag && pt.El > 0) elFlag = 1;
            }
        }
    }
    px = _u1(data.satLon);
    py = _v1(data.satLat);
    var footradius = data.satFootprint / 2.0;
    ctx.fillStyle = "yellow";
    _j1(ctx, px, py, 5);
    if (data.satEL > 0.0) {
        ctx.strokeStyle = "yellow";
    } else {
        ctx.strokeStyle = "red";
    }
    ctx.beginPath();
    ctx.lineWidth = 1.3;
    var lastX, lastY;
    for (bearing = 0; bearing <= 2.1 * 3.14159; bearing += (0.017453278) * 1) {
        var coords = _c3(data.satLat, data.satLon, bearing, footradius * 1);
        y = _v1(coords[0]);
        x = _u1(coords[1]);
        if (x < 0) x = 600 - x;
        if ((bearing == 0) || Math.abs(lastX - x) > 20) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        lastX = x;
        lastY = y;
    }
    ctx.stroke();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "green";
    ctx.fillStyle = "black";
    o = 30;
    p = 20;
    ctx.fillRect(w - o, h - o, p, p);
    ctx.strokeRect(w - o, h - o, p, p);
    ctx.lineWidth = 1.3;
    ctx.strokeStyle = "gray";
    if (strk) ctx.strokeStyle = "cyan";
    ctx.beginPath();
    for (x = w - 10; x > w - o; x -= 2) {
        ctx.lineTo(x, h - 20 - Math.sin((x + 10) / 3) * 7);
    }
    ctx.stroke();
}

function _r1(u) {
    var z = _d('timef').value;
    var utc = !!(z & 2);
    var am = !(z & 1);
    var h, m, s;
    var ams = '';
    var d = new Date(u * 1000);
    if (utc) {
        h = d.getUTCHours();
        m = d.getUTCMinutes();
        s = d.getUTCSeconds();
    } else {
        h = d.getHours();
        m = d.getMinutes();
        s = d.getSeconds();
    }
    if (am) {
        ams = ' AM';
        if (h >= 12) {
            ams = ' PM';
            if (h > 12) h -= 12;
        }
    }
    return h.toString().padStart(2, '0') + ":" + m.toString().padStart(2, '0') + ":" + s.toString().padStart(2, '0') + ams;
}

function _n1(unix) {
    if (unix < 1000) return '--';
    var z = _d('timef').value;
    var utc = !!(z & 2);
    let d = new Date(unix * 1000);
    let ds = d.toLocaleDateString();
    if (utc) {
        ds = (new Date(d.toISOString().slice(0, -1))).toLocaleDateString();
    }
    return ds + " " + _r1(unix);
}

function flipAZ(az) {
    var one80 = 180.0;
    if (az > one80) return az - one80;
    else return az + one80;
}

function _k1(el) {
    return 180.0 - el;
}
var toHHMMSS = (secs) => {
    if (secs > 432000) return '';
    var sec_num = parseInt(secs, 10);
    var h = Math.floor(sec_num / 3600);
    var m = Math.floor(sec_num / 60) % 60;
    var s = sec_num % 60;
    return [h, m, s]
        .map(v => v < 10 ? "0" + v : v)
        .filter((v, i) => v !== "00" || i > 0)
        .join(":");
}

function _a3() {
    drawMap++;
    if (drawMap > 3) drawMap = 0;
    _b2(ldata);
}

function _v1(lat) {
    return 150 - (lat * (150.0 / (3.14159 / 2.0)));
}

function _u1(lon) {
    return 300 + (lon * (300.0 / 3.14159))
}

function _b3(ctx, x, y, r) {
    ctx.beginPath();
    ctx.moveTo(x, y - r);
    ctx.lineTo(x + r, y + r);
    ctx.lineTo(x - r, y + r);
    ctx.lineTo(x, y - r);
    ctx.fill();
    ctx.stroke();
}

function _j1(ctx, x, y, r) {
    ctx.beginPath();
    ctx.moveTo(x, y - r);
    ctx.lineTo(x + r, y);
    ctx.lineTo(x, y + r);
    ctx.lineTo(x - r, y);
    ctx.lineTo(x, y - r);
    ctx.fill();
    ctx.stroke();
}

function dot(ctx, x, y, r) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
}

function _c3(rlat, rlon, rb, rn) {
    ER = 6378.137;
    lat = (Math.asin(Math.sin(rlat) * Math.cos(rn / ER) + Math.cos(rlat) * Math.sin(rn / ER) * Math.cos(rb)));
    lon = (rlon + Math.atan2(Math.sin(rb) * Math.sin(rn / ER) * Math.cos(rlat), Math.cos(rn / ER) - Math.sin(rlat) * Math.sin(lat)));
    return [lat, lon];
}

function togglevisible(se) {
    var v = _d(se);
    var x = _d(se + 'vis');
    if (x.style.display === "block") {
        x.style.display = "none";
        x.setAttribute('data-vis', '2');
        v.classList.remove('popup');
    } else {
        x.style.display = "block";
        x.setAttribute('data-vis', '1');
        v.classList.add('popup');
    }
}

function _d3() {
    var s = new Date().getTime() / 1000;
    s = Math.round(s);
    _f1("T|" + s);
}

function _e3() {
    var v = parseInt(_d('groundtrack').value);
    var el = _d('gtrktype');
    if (el.options[el.selectedIndex].value == 1) v = 0 - v;
    _f1("j|" + v);
    groundTrack = 0;
}

function autocal() {
    if (confirm("** IMPORTANT! PLEASE READ\n\nThe auto-calibration procedure will move your rotator it's FULL ROTATION on both Azimuth and Elevation.\n\nIf you want to stop the calibration while it is in progress you must remove power from the S.A.T.\n\nThe calibration procedure can take up to 4 minutes and the S.A.T. will be unresponsive during this time.")) _f1('Z|a');
}

function caz(p) {
    if (p & 1) {
        _d('az').value = _d('el').value = ''
    };
    if (p & 2) {
        _d('pg').value = ''
    };
    if (p & 4) {
        _d('lt').value = _d('ln').value = ''
    };
}

function _f1(param) {
    var url = '/cmd?a=' + param;
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _h4Loop() {
    t = _h4();
    setTimeout(_h4Loop, t);
}

function _h4() {
    if (!cdata) return 1000;
    url = `http://www.csntechnologies.net/SAT/sstatusJSON.php?ser=${cdata.serial}`;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            satStat = JSON.parse(this.responseText);
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
    return 3600000;
}

function sreport(e) {
    c = cdata;
    if (e.value < 0) return;
    dsc = '';
    for (pt of ldata.freq)
        if (ldata.afreq == pt.uid) dsc = pt.descr;
    url = `http://www.csntechnologies.net/SAT/sreport.php?cat=${ldata.catno}&call=${c.call}&grid=${c.grid}&status=${e.value}&dsc=${dsc}&ser=${c.serial}`;
    xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            _d('message').innerHTML = 'STATUS REPORTED';
            _h4();
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function c_f1(param) {
    m = 'Are you sure';
    c = param.charAt(0);
    if (c == 'M') m += ' you want to set Maximum?';
    else if (c == 'N') m += ' you want to set Minimum?';
    else m += '?';
    if (!confirm(m)) return;
    _f1(param);
}

function savegrd() {
    let r = '';
    Array.from(_d('svgrd').options).forEach(function(e) {
        r += e.value + '^';
    });
    _f1('Z|g|' + r);
}

function addGrd() {
    var o = ce('option');
    l = prompt('Enter Label');
    g = prompt('Enter Grid Square or Azimuth');
    if (g.length >= 0) {
        s = _d('svgrd');
        o.value = l.trim() + ' (' + g.trim() + ')';
        o.text = o.value;
        s.add(o);
        s.value = o.value;
        savegrd();
        grdchg();
    }
}

function rmGrd() {
    v = _d('svgrd').value.trim();
    f = false;
    Array.from(_d('svgrd').options).forEach(function(e) {
        if (v == e.value) {
            f = true;
            e.remove();
            _d('svgrd').value = '';
        }
    });
    if (f) savegrd();
}

function grdchg() {
    v = _d('svgrd').value.trim();
    l = v.lastIndexOf(' (');
    if (l > -1 && v.indexOf(')') == v.length - 1) {
        v = v.substr(l).replace('(', '').replace(')', '').trim();
        if (!isNaN(parseFloat(v))) {
            _d('az').value = v;
            _d('el').value = 0.0;
            _d('pg').value = '';
        } else {
            _d('pg').value = v;
            _q3(v, false, 'manual');
        }
    }
}

function _f3(but) {
    if (gsatsD && but) {
        gsatsD = 0;
        return;
    }
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            try {
                gsats = JSON.parse(this.responseText);
                gsatsD = 1;
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", "/gps", true);
    xhttp.send();
}

function _g3() {
    gl = _d('svgrd');
    if (gl.options.length > 0) return;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            try {
                g = JSON.parse(this.responseText);
                gl.innerHTML = '';
                o = ce('option');
                o.value = '';
                o.text = '';
                gl.add(o);
                g.grds.forEach(s => {
                    if (s != 0) {
                        o = ce('option');
                        o.value = s;
                        o.text = s;
                        gl.add(o);
                    }
                });
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", "/grds", true);
    xhttp.send();
}

function getGroundTrack() {
    var url = '/gtrack';
    if (pauseUpdates.length > 0) return;
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Ground Track";
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                groundTrack = JSON.parse(this.responseText);
                groundTrackTime = new Date().getTime() / 1000;
                windows.forEach(passData);
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _h3() {
    var url = '/path';
    if (pauseUpdates.length > 0) return;
    var xhttp = new XMLHttpRequest();
    pauseUpdates = 'Pause-Get Path';
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                satPath = JSON.parse(this.responseText);
                windows.forEach(passData);
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function getTMin() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            try {
                var data = JSON.parse(this.responseText);
                handleMin(data);
            } catch (e) {
                if (dbg) console.log(e);
                return;
            }
        }
    }
    xhttp.open("GET", "/min", true);
    xhttp.send();
}

function _g1(manual) {
    var url = '/track';
    if (manual) url = "/status";
    if (pauseUpdates.length > 1) return;
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Get Status";
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = "";
            try {
                var data = JSON.parse(this.responseText);
                _c2(data, manual);
                if (data.mode == 1) {
                    setTimeout(getTMin, 2750 * .5);
                }
            } catch (e) {
                if (dbg) console.log(e);
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function setb(ename) {
    if (lastb) lastb.style = lastbs;
    btn = _d(ename);
    lastb = btn;
    lastbs = btn.style;
    btn.style.border = '1px solid #00AA44';
}

function stopp() {
    if (ipan) {
        _f1('S');
        ipan = 0;
    }
}

function stop() {
    _f1('S');
    _d('sstat').value = -1;
    _d('volts').style = 'display: none';
    _d('searchname').value = '';
    groundTrack = 0;
    satPath = 0;
    _q();
    setTimeout(function() {
        _d3();
    }, 1000);
}

function _t1(e, v, t = '') {
    if (v && v != -1) {
        e.style.backgroundColor = '#005500';
        e.style.color = '#99CCFF';
        e.title = t + ' Enabled';
    } else {
        e.style.backgroundColor = '#8e000a';
        e.style.color = '#000000';
        e.title = t + ' Disabled';
    }
}
var aecol = 1;

function aebut() {
    if (ldata) {
        b = _d('btnrotenable');
        if (ldata.rotEnable == 1) {
            _t1(b, 1, 'Rotator');
        } else {
            _t1(b, 0, 'Rotator');
            b.style.backgroundColor = aecol ? '#8e000a' : '#e5000a';
            b.style.color = '#000000';
            aecol = !aecol
        }
    }
    setTimeout(aebut, 1250);
}

function _i3() {
    _f1('x');
    setTimeout(function() {
        _g1(false);
    }, 100);
}

function _j3() {
    _f1('B|E');
    setTimeout(function() {
        _g1(false);
    }, 100);
}

function _k3() {
    continuous = !continuous;
    var b = (continuous == true) ? '1' : '0';
    _f1('c|' + b);
    setTimeout(function() {
        _g1(false);
    }, 100);
}

function _l3() {
    var az, el;
    var e = '';
    if (_d('lt').value) {
        az = _d('lt').value.trim();
        el = _d('ln').value.trim();
        e = '1';
    } else {
        az = _d('az').value.trim();
        el = _d('el').value.trim();
    }
    if (az.length < 1) az = '0';
    if (el.length < 1) el = '0';
    _f1('P|' + az + '|' + el + '|' + e);
}

function _m3() {
    var e = _d("ssid");
    var ssid = e.options[e.selectedIndex].text.trim();
    ssid = ssid.replace(/\|/g, "%X7C");
    console.log(ssid);
    var pass = _d('pass').value.trim();
    pass = pass.replace(/#/g, "%23");
    console.log(pass);
    _f1('W|' + ssid + '|' + pass);
    console.log({
        ssid: ssid,
        pass: pass
    });
    alert("Device will restart and attempt to connect to " + ssid + "\nIf it does not succeed it will revert back to AP mode.")
    hide('divnetwork');
}

function _n3(ip) {
    if (/^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$/.test(ip)) return true;
    return false;
}

function _o3() {
    var localip = _d('localip').value.trim();
    var gateway = _d('gateway').value.trim();
    var subnet = _d('subnet').value.trim();
    var primarydns = _d('primarydns').value.trim();
    var secondarydns = _d('secondarydns').value.trim();
    var ntpserver = _d('ntpserver').value.trim();
    if (!_n3(localip)) {
        alert('Invalid IP address');
        _d('localip').focus();
        return;
    }
    if (!_n3(gateway)) {
        alert('Invalid gateway address');
        _d('gateway').focus();
        return;
    }
    if (!_n3(subnet)) {
        alert('Invalid subnet address');
        _d('subnet').focus();
        return;
    }
    if (!_n3(primarydns)) {
        alert('Invalid primary DNS address');
        _d('primarydns').focus();
        return;
    }
    if (secondarydns.length > 0 && !_n3(secondarydns)) {
        alert('Invalid secondary DNS address');
        _d('secondarydns').focus();
        return;
    }
    _f1('Z|n|' + localip + '|' + gateway + '|' + subnet + '|' + primarydns + '|' + secondarydns + '|' + ntpserver);
    alert("Device will restart.\nIf it does not succeed it will revert back to AP mode.")
    hide('divnetwork');
}

function getssid() {
    var url = '/scanap';
    var xhttp = new XMLHttpRequest();
    var select = _d("ssid");
    var i;
    pauseUpdates = 'Pause-Get Wifi';
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            for (i = select.options.length - 1; i >= 0; i--) {
                select.remove(i);
            }
            if (globalssid) select.options[select.options.length] = new Option(globalssid, '0', false, false);
            var aplist;
            try {
                aplist = JSON.parse(this.responseText);
            } catch (e) {
                return;
            }
            for (x = 0; x < aplist.length; x++) {
                var o = aplist[x];
                if (o.length > 0) select.options[select.options.length] = new Option(o, '0', false, false);
            }
            select.options[select.options.length] = new Option('', '', false, false);
        }
    };
    for (i = select.options.length - 1; i >= 0; i--) {
        select.remove(i);
    }
    select.options[select.options.length] = new Option("Please Wait...", '0', false, false);
    xhttp.open("GET", url, true);
    xhttp.send();
}

function reloadpage() {
    location.reload(true);
}

function update() {
    var wrg = "WARNING-QSO Log Entries Found!\n\nFirmware updates may corrupt your QSO Log. Click Cancel stop the update so you can download your log. Click Ok to continue with the update.";
    if (qsolog || 0) {
        if (qsolog.log.length > 1) {
            if (!confirm(wrg)) return;
        }
    }
    if (!confirm(fwWarning)) return;
    _f1("I");
    _d('btnupdate').value = ' Please Wait... ';
    pauseUpdates = 'Pause-FW Update';
    setTimeout(reloadpage, 10000);
}

function updateTLE() {
    _d3();
    satList = 0;
    var tleurl = _d('tleurl').value.trim();
    var http = tleurl.substr(0, 5).toLowerCase();
    if (http == 'https') {
        alert("HTTPS addresses are not supported at this time.\n\nUsually you can simply remove the 's' from the 'https' part of the address\n\nIf that does not work you'll need to download the file manually and use the UPLOAD feature below.");
        return;
    }
    _f1('Y|' + tleurl);
}

function _p3() {
    _d('call').value = _d('call').value.substring(0, 16);
    _f1('L|' + _d('lat').value.trim() + '|' + _d('lon').value.trim() + '|' + _d('call').value.trim() + '|' + _d('grid').value.trim() + '|' + _d('lcdunits').value.trim() + '|' + _d('timef').value.trim() + '|' + _d('gpsen').value.trim() + '|X');
}

function _q3(loc, warn, gtype) {
    loc = loc.toString().toUpperCase();
    var x_l, x_m, x_r, y_l, y_m, y_r;
    var letters = "ABCDEFGHIJKLMNOPQRSTUVWX";
    var radius = 6378.16;
    var ff;
    if (loc.length == 4) {
        loc += "MM";
        ff = false;
    } else ff = true;
    if (loc.length != 6) {
        if (warn) alert("The locator must have 4 chars i.e. JN68 or jn59 or 6 chars i.e. JN68RN or jn59eg");
        return (false);
    }
    x_l = letters.indexOf(loc.charAt(0));
    x_m = parseInt(loc.charAt(2));
    x_r = letters.indexOf(loc.charAt(4));
    y_l = letters.indexOf(loc.charAt(1));
    y_m = parseInt(loc.charAt(3));
    y_r = letters.indexOf(loc.charAt(5));
    if (x_l < 0 || x_l > 17 || y_l < 0 || y_l > 17 || isNaN(x_m) || isNaN(y_m) || x_r < 0 || x_r > 23 || y_r < 0 || y_r > 23) {
        if (warn) alert("The grid locator must be in the range of AA00AA .... RR99XX");
        return (false);
    }
    x = x_l * 10 + x_m + x_r / 24;
    if (ff) x = x + 1 / 48;
    x *= 2;
    x -= 180;
    y = y_l * 10 + y_m + y_r / 24;
    if (ff) y = y + 1 / 48;
    y -= 90;
    if (gtype == 'setting') {
        _d('lat').value = Math.ceil(y * 10000) / 10000;
        _d('lon').value = Math.ceil(x * 10000) / 10000;
    } else {
        _r3(Math.ceil(y * 10000) / 10000, Math.ceil(x * 10000) / 10000);
    }
    return true;
}

function _r3(dlat, dlon) {
    startLat = parseFloat(_d('lat').value) * (Math.PI / 180.0);
    startLng = parseFloat(_d('lon').value) * (Math.PI / 180.0);
    destLat = dlat * (Math.PI / 180.0);
    destLng = dlon * (Math.PI / 180.0);
    y = Math.sin(destLng - startLng) * Math.cos(destLat);
    x = Math.cos(startLat) * Math.sin(destLat) - Math.sin(startLat) * Math.cos(destLat) * Math.cos(destLng - startLng);
    brng = Math.atan2(y, x);
    brng = brng * (180.0 / Math.PI);
    while (brng < 0.0) brng += 360.0;
    while (brng > 360.0) brng -= 360.0;
    _d('az').value = brng.toFixed(1);
    if (!_d('el').value) _d('el').value = '0.0';
}

function _s3() {
    var g = _d('autotle').value.trim();
    _f1('s|' + g);
}

function _t3() {
    pauseUpdate = true;
    pass = _d('qrzp').value.trim();
    pass = pass.replace(/#/g, "%23");
    _f1("V|" + _d('tzoffset').value.trim() + '|' + _d('qrzl').value.trim() + '|' + pass + '|x|x|' + _d('wkey').value.trim());
}

function _u3() {
    _f1('t|' + _d('toleranceAZ').value.trim() + '|' + _d('toleranceEL').value.trim() + '|X');
    _f1('a|' + _d('antqual').value.trim() + '|X');
    _f1('l|' + _d('parkAZ').value.trim() + '|' + _d('parkEL').value.trim() + '|' + _d('readyAZ').value.trim() + '|' + _d('readyEL').value.trim() + '|' + _d('postpass').value + '|X');
    _v3()
    _f1('i|' + _d('enRelay').value + '|X');
    hide('divrotator')
    _a2();
}

function _a2(snd = 1) {
    var v = _d('rotatorType').value;
    var w = _d('antflip').value;
    var x = _d('rotip').value;
    var y = _d('minpass').value;
    var z = _d('psts').value;
    if (snd) _f1('k|' + v + '|' + w + '|' + x + '|' + y + '|' + z + '|');
    vl = (v == 1) || (v == 2) || (v == 3) || (v == 4) || (v == 6) || (v == 7);
    au = (v == 1) || (v == 2) || (v == 6) || (v == 7);
    bm = _d('btnsetmin');
    bx = _d('btnsetmax');
    bv = _d('btnvolts');
    bc = _d('btnautoc');
    bm.style.color = bx.style.color = bv.style.color = vl ? 'lime' : 'gray';
    bm.disabled = bx.disabled = bv.disabled = !vl;
    bc.style.color = au ? 'lime' : 'gray';
    bc.disabled = !au;
    if (v == 5) {
        _d('pstsr').style.display = _d('pstr2').style.display = 'block';
    } else {
        _d('pstsr').style.display = _d('pstr2').style.display = 'none';
    }
}

function _v3() {
    var a = '1';
    var b = _d('playalarm').value;
    var c = 0;
    var d = _d('aosbeepdeg').value;
    var e = 0;
    var s = 0;
    if (d.indexOf(':') > -1) {
        var sd = d.split(":");
        d = 0;
        if (!isNaN(parseInt(sd[0]))) d = parseInt(sd[0]) * 60;
        if (!isNaN(parseInt(sd[1]))) d += parseInt(sd[1]);
    }
    _f1('E|' + a + '|' + b + '|' + c + '|' + d + '|' + e);
}

function _w3(b) {
    _f1('Z|X|' + b.value);
}

function saverad() {
    var el = _d('radtype');
    var a = el.options[el.selectedIndex].value;
    el = _d('radbaud');
    var b = el.options[el.selectedIndex].value;
    var c = parseInt('0x' + _d('radaddress').value.replace('h', ''));
    el = _d('radvfo');
    var d = el.options[el.selectedIndex].value;
    var e = _d('radinterval').value;
    var f = _d('radminf').value;
    var g = _d('radip').value;
    var h = _d('radprt').value;
    _f1('e|' + a + '|' + b + '|' + c + '|' + d + '|' + e + '|' + f + '|' + g + '|' + h);
    hide('divrig');
    _f1('Z|r|' + _d('rap').value + '|' + (_d('rapf').value * 1000000) + '|' + _d('rapm').value + '|' + _d('rapp').value + '|' + _d('ts').value);
    setTimeout(_j2, 2000);
}

function search() {
    _d('sstat').value = -1;
    var s = _d('searchname').value.trim().toUpperCase();
    if (s.length < 1) return;
    _f1('U|' + s);
    gsatsD = 0;
    _d('sbut').focus();
    groundTrack = groundoffset = satPath = 0;
    strk = 1;
    ldata = 0;
    setTimeout(function() {
        _g1(false);
    }, 200);
    _q();
}

function _z3() {
    _f1('n|' + _d('tcpPort').value + '|' + _d('tcpPortRig').value);
}

function _y3() {
    _f1('o');
    _d('volts').style = 'display:block';
    var msg = 'ROTATOR CALIBRATION\n\nThe S.A.T. is now displaying voltages sensed from your rotator control box.\n\nManually set antenna postions to maximum azizmuth and elevation.\n\nAdjust your rotator control box so both AZ and EL voltages are as high as possible but under 5 volts.\n\nWhen adjustments are made, press SET MAX.\n\nThen move your rotator to its minimum azimuth and elevation (-180 AZ for G5400). Then press SET MIN.\n\nPress STOP to exit Volts mode. ';
    alert(msg);
}

function _a4() {
    var serial = _d('serial').innerHTML;
    var xhttp = new XMLHttpRequest();
    subchk = 0;
    url = "http://www.csntechnologies.net/SAT/subchk.php?serial=" + serial + "&version=" + _d('fw').innerHTML;
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            d = JSON.parse(this.responseText);
            console.log(d);
            sub = d.sub;
            if (sub) _d('subrow').style.display = 'block';
            if (sub && suben) _i1(false);
            if (d.fw > parseFloat(_d('fw').innerHTML)) {
                s = ' (Update Available)';
                document.title = 'S.A.T.' + s;
                _d('fw').innerHTML = _d('fw').innerHTML.substring(0, 5) + s;
                _d('btnupdate').value = ' UPDATE ';
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _i1(showResults, useOnline = true, attempt = 1) {
    var tnow = new Date().getTime() / 1000;
    if (showResults && (tnow - lastPredict) < 60) {
        if (predictList) {
            _c4(predictList);
            return;
        }
    }
    if (!satList) {
        _p1 = _i1;
        _e4(false);
        return;
    }
    var fav = ";";
    if (satList.favs?.length > 0) {
        satList.favs.forEach(f => {
            fav += f + ";";
        });
    } else {
        satList.sats.forEach(f => {
            fav += f.ID + ";";
        });
    }
    ymsg("Looking for Passes...");
    var url = "/future?a=" + fav;
    if (useOnline && sub && suben) {
        var serial = _d('serial').innerHTML;
        xlat = _d('lat').value;
        xlon = _d('lon').value;
        if (ldata.gpsav && ldata.gpsen && ldata.gpslock) {
            xlat = ldata.gpslat;
            xlon = ldata.gpslon;
        }
        url = "http://www.csntechnologies.net/SAT/Predict/predict.php?hours=12&a=" + fav + "&lat=" + xlat + "&lon=" + xlon + "&serial=" + serial;
    }
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Get Future";
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            pauseUpdates = '';
            try {
                predictList = JSON.parse(this.responseText);
                if (predictList) {
                    predictList.list = predictList.list.sort(_dx);
                }
                lastPredict = new Date().getTime() / 1000;
                if (showResults) _c4(predictList);
                windows.forEach(passData);
            } catch (e) {
                console.log(e);
                if (attempt > 1) {
                    sub = 0;
                    return;
                }
                sub = 0;
                _i1(showResults, false, attempt + 1)
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _b4(showResults) {
    var tnow = new Date().getTime() / 1000;
    if ((tnow - lastPredict) < 60 * 3) {
        if (predictList) {
            _c4(predictList);
            return;
        }
    }
    var url = '/future';
    var xhttp = new XMLHttpRequest();
    pauseUpdates = 'Pause-getFuture';
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                var data = JSON.parse(this.responseText);
                predictList = data;
                lastPredict = new Date().getTime() / 1000;
                if (showResults) _c4(predictList);
                windows.forEach(passData);
            } catch (e) {
                return;
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function gsstat($cat, $obj = 0) {
    if (!satStat[$cat]) {
        if ($obj == 1) return 0;
        if ($obj == 2) return document.createElement('a');
        return '';
    }
    s = satStat[$cat];
    tm = _n1(s.time);
    s.txtime = tm;
    if ($obj == 1) {
        return s;
    }
    if ($obj == 2) {
        sdot = document.createElement('a');
        sdot.setAttribute('href', s.url);
        sdot.setAttribute('target', 'stat');
        sdot.style.color = s.col;
        sdot.style.fontSize = s.sz + 'em';
        sdot.style.textDecoration = 'none';
        sdot.innerHTML = s.shape + ' ';
        sdot.title = `${s.txtime}${s.pop}`;
        return sdot;
    }
    st = `<a href='${s.url}' target='stat' title='${s.txtime}${s.pop}' style="color:${s.col};text-decoration:none;font-size:${s.sz}em">${s.shape}</a>`;
    return st;
}

function _c4(data) {
    _d('id01').style.display = 'block';
    var satdiv = _d('satdiv');
    satdiv.innerHTML = '';
    minEl = parseFloat(_d('minpass').value);
    //if(data) {data.sats=data.sats.sort(cmp);}
    var count = 1;
    var cs = document.querySelectorAll('canvas');
    var tnow = new Date().getTime() / 1000;
    listCopy = JSON.parse(JSON.stringify(data.list));
    limit = 50;
    sats = [];
    listCopy.forEach(s => {
        aost = 0;
        if (sats.indexOf(s[9]) > -1) {
            aost = s[2];
        } else {
            sats.push(s[9]);
        }
        if ((s[7] >= minEl) && (ldata.time < s[3]) && ((limit--) > 0)) {
            var c;
            var sel = '<br>&nbsp;';
            var dir = '';
            var div = ce("div");
            div.classList.add("satitem");
            ar = '';
            if (s[11] == 0) ar = '&uarr;'
            else if (s[11] == 1) ar = '&darr;'
            sel = `<br><b>EL NOW:</b>${s[8]}&deg; <span style='font-size:1.6em'>${ar}</span>`;
            var sdur = "";
            if (s[4] > 0) {}
            sdur = "<br><b>DUR</b> " + s[4];
            if ((s[7] > 0 && s[8] < 0) || (tnow < s[2])) {
                c = hslToHex(20, (s[7] / 120.0) + 0.25, 0.5); //org
            } else {
                c = hslToHex(120, (s[8] / 106.0) + 0.15, 0.4);
            }
            if (!isNaN(s[2]))
                s[2] = _r1(s[2]);
            if (!isNaN(s[3]))
                s[3] = _r1(s[3]);
            st = gsstat(s[9], 0);
            var imgsrc = _d('reportico').src;
            var i = `<img stype='cursor:default;padding-left:5px' src='${imgsrc}' title="Click for Future Pass Report" onclick="_f('${s[9]}');event.preventDefault();">`;
            div.innerHTML = `<h3>${st} <span onclick='_d4("${s[1]}", "${s[9]}",${aost})' style='margin-top:0px;' ><u>${s[1]}</u></span> ${i}</h3><b>AOS:</b> ${s[2]}<br><b>LOS:</b> ${s[3]}${sdur}<br><b>MAX EL:</b> ${s[7]}&deg; ${sel}<br>`;
            satdiv.appendChild(div);
            div.style.backgroundColor = c;
            if (Array.isArray((s[11] || 0))) s[10] = s[11];
            if (s[10].length > 1) {
                c = _q1(s, s[9]);
                var dv = ce("div");
                dv.style.width = '100%';
                dv.style.textAlign = 'center'
                dv.appendChild(c);
                div.appendChild(dv);
            }
        }
    });
}

function _q1(a, id) {
    var c = document.createElement('canvas');
    c.style.textAlign = 'center';
    c.style.border = '2px solid #00000088';
    c.style.borderRadius = '8px';
    c.style.backgroundColor = '#00000077';
    var ctx = c.getContext("2d");
    c.id = 'polar' + id;
    w = 160;
    h = 160;
    c.width = h * 1.8;
    c.height = h;
    var center_h = h / 2;
    var r = center_h - 3;
    var center_w = r + 5;
    var exey = {
        ex: 0,
        ey: 0
    };
    ctx.lineWidth = 1;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = "black";
    ctx.fillStyle = '#000000DD';
    ctx.arc(center_w, center_h, r, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    ctx.strokeStyle = "gray";
    ctx.lineWidth = 0.75;
    ctx.beginPath();
    ctx.arc(center_w, center_h, r * ((90.0 - 60) / 90.0), 0, 2 * Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(center_w, center_h, r * ((90.0 - 30) / 90.0), 0, 2 * Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(center_w, center_h - r);
    ctx.lineTo(center_w, center_h + r);
    ctx.moveTo(center_w - r, center_h);
    ctx.lineTo(center_w + r, center_h);
    ctx.stroke();
    _j(a[10][0][1], a[10][0][2], center_w, center_h, r, exey);
    lx = exey.ex;
    ly = exey.ey;
    ctx.lineWidth = 3.5;
    lastEL = 0;
    ctx.strokeStyle = 'green';
    a[10].forEach(p => {
        if (p[0] > 0) {
            ctx.beginPath();
            ctx.moveTo(lx, ly);
            _j(p[1], p[2], center_w, center_h, r, exey);
            if (p[2] < lastEL) ctx.strokeStyle = 'red';
            ctx.lineTo(exey.ex, exey.ey);
            ctx.stroke();
            lx = exey.ex;
            ly = exey.ey;
            lastEL = p[2];
        }
    });
    ctx.beginPath();
    ctx.fillStyle = 'white';
    ctx.font = "15px sans-serif";
    ctx.fillText("AOS: " + a[5] + "°", center_w + r + 10, 20);
    ctx.fillText("LOS: " + a[6] + "°", center_w + r + 10, 40);
    ctx.stroke();
    return c;
}

function cmp(a, b) {
    return a.aosTimeUTC - b.aosTimeUTC;
}

function ce(e) {
    return document.createElement(e);
}

function hslToHex(h, s, l) {
    h /= 360;
    let r, g, b;
    if (s === 0) {
        r = g = b = l; // achromatic
    } else {
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1 / 6) return p + (q - p) * 6 * t;
            if (t < 1 / 2) return q;
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
            return p;
        };
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        r = hue2rgb(p, q, h + 1 / 3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1 / 3);
    }
    const toHex = x => {
        const hex = Math.round(x * 255).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    };
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function ymsg(msg) {
    _d('message').innerHTML = "<span style='background-color:yellow;color:black'>" + msg + "</span>";
    clearmsg = 1;
}

function _d4(s, catnr, aost = 0) {
    _q();
    groundTrack = 0;
    satPath = 0;
    _d('id01').style.display = 'none';
    _d('searchname').value = s;
    ymsg("Loading " + s);
    if (aost) {
        _d('searchname').value = `${s} @ ` + _r1(aost);
        _f1(`Z|U|${catnr}|${aost}|${s}`);
    } else {
        _f1('U|' + catnr);
        gsatsD = 0;
    }
}

function cmpA(a, b) {
    return a.Name.localeCompare(b.Name);
}

function _e4(openwindow) {
    if (satList) {
        if (openwindow) _o1(satList);
        return;
    }
    var url = '/viewtle';
    var xhttp = new XMLHttpRequest();
    pauseUpdates = '';
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                var data = JSON.parse(this.responseText);
                if (data) {
                    data.sats = data.sats.sort(cmpA);
                }
                satList = data;
                if (openwindow) _o1(data);
                windows.forEach(passData);
                if (_p1) {
                    _p1(true);
                    _p1 = 0;
                }
            } catch (e) {
                console.log(e);
                return;
            }
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _o1(data) {
    _d('id02').style.display = 'block';
    var tdiv = _d('tlediv');
    tlediv.innerHTML = '';
    t = data.sats.filter(x => x.Name.length > 0);
    cols = 4;
    rows = Math.ceil(t.length / cols);
    tab = ce('table');
    tab.style.width = '100%';
    for (rw = 0; rw < rows; rw++) {
        tr = ce('tr');
        tab.appendChild(tr);
        for (cl = 0; cl < cols; cl++) {
            idx = (cl * rows) + rw;
            s = t[idx] || 0;
            if (s && (s.Name || 0)) {
                var d = ce('td');
                var c = ce("input");
                var l = ce("label");
                c.type = "checkbox";
                c.name = "sat" + s.ID;
                c.value = s.ID;
                c.id = 't' + s.ID;
                l.style.cursor = 'pointer';
                l.setAttribute('sid', s.ID);
                l.setAttribute('sn', s.Name);
                l.addEventListener('click', function(event) {
                    _d4(this.getAttribute('sn'), this.getAttribute('sid'));
                    _d('id02').style.display = 'none'
                });
                l.appendChild(document.createTextNode(s.Name + ' '));
                i = ce('img');
                i.setAttribute('src', _d('reportico').src);
                i.setAttribute('sid', s.ID);
                i.setAttribute('title', 'Click for Future Pass Report');
                i.style.cursor = 'default';
                i.addEventListener('click', function(event) {
                    _f(this.getAttribute('sid'));
                    event.preventDefault();
                    return false;
                }, false);
                if (s.ID == 'MOON' || s.ID == 'SUN') {
                    i.style.display = c.style.display = 'none';
                }
                sdot = gsstat(s.ID, 2);
                d.appendChild(c);
                d.appendChild(l);
                if (sdot) {
                    d.appendChild(sdot);
                }
                d.appendChild(i);
                tr.appendChild(d);
            }
        }
    }
    tdiv.appendChild(tab);
    data.favs.forEach(f => {
        document.getElementById('t' + f).checked = true;
    })
}

function _a() {
    var list = document.querySelectorAll("[name^='sat']");
    list.forEach(element => {
        element.checked = true;
    });
}

function un_a() {
    var list = document.querySelectorAll("[name^='sat']");
    list.forEach(element => {
        element.checked = false;
    });
}

function _c() {
    var list = document.querySelectorAll("[name^='sat']:checked");
    var fav = ";";
    list.forEach(element => {
        fav += element.value + ";";
    });
    _f1('g|' + fav);
    satList = 0;
    setTimeout(function() {
        _e4(false);
    }, 2000);
    _d('id02').style.display = 'none';
}

function _dx(a, b) {
    return a[2] - b[2];
}

function _e(jsonreport, w) {
    var d = w.document;
    d.body.innerHTML = '';
    d.write("<style>* {font-family: \"courier new\", courier, monospace; font-size: 14pt;} @media print {*{font-size: 8pt; } button { display:none; } }</style><body>");
    d.write("<span style='white-space: pre;'>");
    d.write("SATELLITE PASS REPORT by CSN Technologies S.A.T.\n");
    n = _n1(new Date().getTime() / 1000);
    d.write("Generated on " + n + "\nGrid Square: " + _d('grid').value + " Lat/Lon " + _d('lat').value + ", " + _d('lon').value + "\n\n");
    d.write("Pass Satellite         AOS                      LOS                      DUR       AOS AZ   LOS AZ   MAX EL\n");
    d.write("---- ----------------- ------------------------ ------------------------ --------- -------- -------- -------\n");
    minEl = parseFloat(_d('minpass').value);
    var line = 1;
    jsonreport.list.forEach(e => {
        if (e[0] && e[7] >= minEl) {
            e[2] = _n1(e[2]);
            e[3] = _n1(e[3]);
            sline = line.toString().padEnd(5, ' ');
            e[1] = e[1].substr(0, 17).padEnd(18, ' ');
            e[2] = e[2].padEnd(25, ' ');
            e[3] = e[3].padEnd(25, ' ');
            e[4] = e[4].padEnd(10, ' ');
            e[5] = e[5].toString().padEnd(9, ' ');
            e[6] = e[6].toString().padEnd(9, ' ');
            e[7] = e[7].toString().padEnd(6, ' ');
            d.write(`${sline}${e[1]}${e[2]}${e[3]}${e[4]}${e[5]}${e[6]}${e[7]}\n`);
            line++;
        }
    });
    d.write("\nGenerated on " + n + "\nCSN Technologies S.A.T.");
    d.write("</span><br><br><button onclick='window.print()' >PRINT</button> <button onclick='window.close()' >CLOSE</button></body>");
}

function _f(catno, useOnline = true, attempts = 1) {
    var list = document.querySelectorAll("[name^='sat']:checked");
    var fav = ";";
    list.forEach(element => {
        fav += element.value + ";";
    });
    var url = "/report?a=" + fav;
    if (catno) url = "/report?a=" + catno;
    if (useOnline) {
        var serial = _d('serial').innerHTML;
        url = "http://www.csntechnologies.net/SAT/Predict/predict.php?hours=120&a=" + fav + "&lat=" + _d('lat').value + "&lon=" + _d('lon').value + "&serial=" + serial;
        if (catno) url = "http://www.csntechnologies.net/SAT/Predict/predict.php?hours=120&a=" + catno + "&lat=" + _d('lat').value + "&lon=" + _d('lon').value + "&serial=" + serial;
    }
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Get Report";
    w = window.open('', 'report', "width=1500,height=768");
    var d = w.document;
    d.write('Please wait...');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                jsonreport = JSON.parse(this.responseText);
                if (jsonreport) {
                    jsonreport.list = jsonreport.list.sort(_dx);
                }
                _e(jsonreport, w);
            } catch (e) {
                if (attempts > 1) return;
                _f(catno, false, attempts + 1)
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _m1(data) {
    var c = _d('cTrack3');
    var ctx = c.getContext("2d");
    c.width = 600;
    c.height = 300;
    data.az = _i(data.az);
    var w = c.width;
    var h = c.height;
    var center_w = w / 2;
    var center_h = h / 2;
    var ground = h - (.15 * h);
    var skyheight = (.85 * h)
    var r = (w > h) ? center_h - 5 : center_w - 5;
    var lookAt = 0;
    if (data.satAZ) lookAt = parseFloat(data.satAZ);
    else lookAt = parseFloat(data.az);
    lookAt += groundoffset;
    var spanAZ = 170.0;
    var leftAZ = _i(lookAt - spanAZ / 2.0);
    var rightAZ = _i(lookAt + spanAZ / 2.0);
    var x, y;
    var markerSize = 8;
    var fontSize = 16;
    var legendTop = ground + 41;

    function _g(az) {
        if (leftAZ > rightAZ && az < rightAZ)
            az = parseFloat(az) + 360.0;
        da = (az - leftAZ);
        var r = (da / spanAZ) * w;
        return r * 1;
    }

    function _h(el) {
        if (el < 0) return ground;
        else if (el > 90) return 0;
        var r = ground - ((el / 90.0) * skyheight)
        return r * 1;
    }

    function _i(iaz) {
        while (iaz >= 360) iaz -= 360.0;
        while (iaz < 0) iaz += 360.0;
        return iaz;
    }
    ctx.clearRect(0, 0, w, h);
    ctx.lineWidth = 1;
    ctx.fillStyle = "black";
    ctx.fillRect(0, ground, w, .15 * h);
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, w, skyheight);
    // draw compass
    ctx.font = fontSize + "px sans-serif"
    ctx.strokeStyle = "white";
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    var xa = leftAZ;
    var count = 0;
    while (count++ < spanAZ) {
        xa = xa.toFixed();
        var lh = 0;
        if ((xa % 15) == 0 || (xa == 90) || (xa == 270)) {
            lh = 10
        } else if ((xa % 5) == 0) {
            lh = 5
        }
        if (lh > 0) {
            var x = _g(xa);
            ctx.beginPath()
            ctx.moveTo(x, ground);
            ctx.lineTo(x, ground + lh);
            ctx.stroke();
            if (lh == 10) {
                var t = _i(xa);
                var c = 'white';
                var cb = '#000055';
                switch (t) {
                    case 0:
                        t = 'N';
                        c = cb;
                        break;
                    case 45:
                        t = 'NE';
                        c = cb;
                        break;
                    case 90:
                        t = 'E';
                        c = cb;
                        break;
                    case 135:
                        t = 'SE';
                        c = cb;
                        break;
                    case 180:
                        t = 'S';
                        c = cb;
                        break;
                    case 225:
                        t = 'SW';
                        c = cb;
                        break;
                    case 270:
                        t = 'W';
                        c = cb;
                        break;
                    case 315:
                        t = 'NW';
                        c = cb;
                        break;
                }
                ctx.fillStyle = c;
                ctx.fillText(t, x, ground + 24);
            }
        }
        xa = (xa * 1) + 1;
    }
    // draw ver axis
    ctx.strokeStyle = "blue";
    ctx.fillStyle = "white";
    for (ya = 15; ya < 90; ya += 15) {
        ctx.beginPath();
        var y = _h(ya);
        ctx.moveTo(28, y);
        ctx.lineTo(w, y);
        ctx.stroke();
        ctx.fillText(ya + '°', 13, y + 3);
    }
    //if(!data) return;
    if (data.mode != 1) return;
    //if(data.path === undefined) return;
    if (!satPath) {
        _h3();
    }
    // draw path
    if (satPath instanceof Object) {
        pt = satPath.path[0];
        x = _g(pt[0]);
        y = _h(pt[1]);
        ctx.lineWidth = 2;
        var drawLine = false;
        for (pt of satPath.path) {
            if (pt[0] >= 0) {
                ctx.beginPath();
                ctx.moveTo(x, y);
                x = _g(pt[0]);
                y = _h(pt[1]);
                if (x >= 0 && x <= w) {
                    if (drawLine) {
                        ctx.lineTo(x, y);
                    } else {
                        ctx.moveTo(x, y);
                        drawLine = true;
                    }
                }
                if (pt[3]) ctx.strokeStyle = "lime";
                else ctx.strokeStyle = "yellow";
                ctx.stroke();
            }
        }
        ctx.lineWidth = 1;
    }
    if (data.aosAZ) {
        ctx.fillStyle = "lime";
        ctx.strokeStyle = "black";
        dot(ctx, _g(data.aosAZ), _h(0), markerSize);
        x = 30;
        y = legendTop; //ground+33;
        dot(ctx, x, y - 4, markerSize);
        ctx.fillStyle = "yellow";
        ctx.fillText("AOS", (x += 30), y + 3);
        ctx.fillStyle = "red";
        ctx.strokeStyle = "black";
        dot(ctx, _g(data.losAZ), _h(0), markerSize);
        x += 36;
        dot(ctx, x, y - 4, markerSize);
        ctx.fillStyle = "yellow";
        ctx.fillText("LOS", (x += 30), y + 3);
    }
    var aaz = data.az;
    var ael = data.el;
    if (data.flipped == 1) {
        aaz = flipAZ(aaz);
        ael = _k1(ael);
    }
    ctx.fillStyle = "transparent";
    if (data.flipped == 1) {
        ctx.strokeStyle = "#ff33cc";
        ctx.fillStyle = "#ff33cc";
    } else {
        ctx.strokeStyle = "#ff6600";
        ctx.fillStyle = "#ff6600";
    }
    ctx.fillRect(_g(aaz) - markerSize, _h(ael) - markerSize, markerSize * 2, markerSize * 2);
    x += 36;
    ctx.fillRect(x, y - 12, markerSize * 2, markerSize * 2 + 15);
    ctx.fillStyle = "yellow";
    ctx.fillText("Antenna", (x += 50), y + 3);
    if (data.mode == 1) {
        if (data.satEL < 0.0) {
            ctx.strokeStyle = "red";
            var c = -(data.satEL / 30.0);
            ctx.fillStyle = hslToHex(1, 0.3, 1 - c);
        } else {
            ctx.fillStyle = "white";
            ctx.strokeStyle = "black";
        }
        _j1(ctx, _g(data.satAZ), _h(data.satEL), markerSize);
        x += 54;
        _j1(ctx, x, y - 4, markerSize);
        ctx.fillStyle = "yellow";
        ctx.fillText("Satellite", (x += 40), y + 3);
    }
}

function _j(az, el, centerx, centery, rad, exey) {
    var a = (az + azmapoffset) * degtorad;
    var r = Math.abs(rad * ((90.0 - el) / 90.0));
    exey.ex = centerx + (Math.sin(a) * r);
    exey.ey = centery + (-Math.cos(a) * r);
}

function _s1(ctx, data) {
    var cx = 31;
    var cy = 300 - 42;
    var r = 30;
    var exey = {
        ex: 0,
        ey: 0
    };
    ctx.strokeStyle = "white";
    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.strokeStyle = "#444444";
    ctx.beginPath();
    ctx.arc(cx, cy, r * ((90.0 - 60) / 90.0), 0, 2 * Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy, r * ((90.0 - 30) / 90.0), 0, 2 * Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx - r, cy);
    ctx.lineTo(cx + r, cy);
    ctx.moveTo(cx, cy - r);
    ctx.lineTo(cx, cy + r);
    ctx.stroke();
    var aaz = data.az;
    var ael = data.el;
    if (data.flipped == 1) {
        aaz = flipAZ(aaz);
        ael = _k1(ael);
    }
    _j(aaz, ael, cx, cy, r, exey);
    ctx.beginPath();
    ctx.strokeStyle = "lime";
    ctx.lineWidth = 1;
    ctx.arc(cx, cy, 0.75, 0, 2 * Math.PI);
    ctx.lineWidth = 4;
    ctx.moveTo(cx, cy);
    ctx.lineTo(exey.ex, exey.ey);
    ctx.stroke();
    ctx.lineWidth = 2;
    if (data.satAZ) {
        _j(data.satAZ, data.satEL, cx, cy, r, exey);
        ctx.strokeStyle = "yellow";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(exey.ex, exey.ey, 2, 0, 2 * Math.PI);
        ctx.stroke();
    }
    ctx.lineWidth = 2;
}

function _l1(data) {
    var c = _d('cTrack2');
    c.width = 600;
    c.height = 300;
    var ctx = c.getContext("2d");
    var w = c.width;
    var h = c.height;
    var center_w = w / 2 - (w / 6);
    var center_h = h / 2;
    var r = (w > h) ? center_h - 5 : center_w - 5;
    var markerSize = 8;
    var fontSize = 20;
    var legendTop = 28;
    var legendLeft = 34;
    var exey = {
        ex: 0,
        ey: 0
    };
    ctx.lineWidth = 1;
    ctx.clearRect(0, 0, w, h);
    ctx.beginPath();
    ctx.strokeStyle = "white";
    ctx.arc(center_w, center_h, r, 0, 2 * Math.PI);
    ctx.fillStyle = "black";
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.lineWidth = 0.75;
    ctx.arc(center_w, center_h, r * ((90.0 - 60) / 90.0), 0, 2 * Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.lineWidth = 0.75;
    ctx.arc(center_w, center_h, r * ((90.0 - 30) / 90.0), 0, 2 * Math.PI);
    ctx.stroke();
    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.strokeStyle = "white";
    ctx.font = (fontSize * .6) + "px sans-serif";
    ctx.fillStyle = "yellow";
    ctx.textAlign = "center";
    _j(360 - 45, 30, center_w, center_h, r, exey);
    ctx.fillText("30", exey.ex, exey.ey);
    _j(360 - 45, 60, center_w, center_h, r, exey);
    ctx.fillText("60", exey.ex, exey.ey);
    ctx.beginPath();
    ctx.lineWidth = 1;
    ctx.strokeStyle = "white";
    ctx.fillStyle = "yellow";
    _j(30, 0, center_w, center_h, r, exey);
    ctx.fillText("30", exey.ex - 4, exey.ey + 12);
    ctx.moveTo(exey.ex, exey.ey);
    _j(180 + 30, 0, center_w, center_h, r, exey);
    ctx.fillText("210", exey.ex + 7, exey.ey - 4);
    ctx.lineTo(exey.ex, exey.ey);
    _j(60, 0, center_w, center_h, r, exey);
    ctx.fillText("60", exey.ex - 8, exey.ey + 8);
    ctx.moveTo(exey.ex, exey.ey);
    _j(180 + 60, 00, center_w, center_h, r, exey);
    ctx.fillText("240", exey.ex + 10, exey.ey - 3);
    ctx.lineTo(exey.ex, exey.ey);
    _j(90 + 30, 0, center_w, center_h, r, exey);
    ctx.fillText("120", exey.ex - 10, exey.ey - 3);
    ctx.moveTo(exey.ex, exey.ey);
    _j(270 + 30, 00, center_w, center_h, r, exey);
    ctx.fillText("300", exey.ex + 10, exey.ey + 8);
    ctx.lineTo(exey.ex, exey.ey);
    _j(90 + 60, 0, center_w, center_h, r, exey);
    ctx.fillText("150", exey.ex - 4, exey.ey - 4);
    ctx.moveTo(exey.ex, exey.ey);
    _j(270 + 60, 00, center_w, center_h, r, exey);
    ctx.fillText("330", exey.ex + 6, exey.ey + 12);
    ctx.lineTo(exey.ex, exey.ey);
    _j(0, 0, center_w, center_h, r, exey);
    ctx.fillText("0", exey.ex - 10, exey.ey - 3);
    ctx.moveTo(exey.ex, exey.ey);
    _j(180, 00, center_w, center_h, r, exey);
    ctx.fillText("180", exey.ex + 10, exey.ey + 8);
    ctx.lineTo(exey.ex, exey.ey);
    _j(90, 0, center_w, center_h, r, exey);
    ctx.fillText("90", exey.ex - 10, exey.ey - 3);
    ctx.moveTo(exey.ex, exey.ey);
    _j(270, 00, center_w, center_h, r, exey);
    ctx.fillText("270", exey.ex + 10, exey.ey + 8);
    ctx.lineTo(exey.ex, exey.ey);
    ctx.stroke();
    ctx.beginPath();
    ctx.font = fontSize + "px sans-serif";
    ctx.fillStyle = "yellow";
    ctx.textAlign = "center";
    _j(0 + 3, 0, center_w, center_h, r - 16, exey);
    ctx.fillText("N", exey.ex, exey.ey);
    _j(90 + 3, 0, center_w, center_h, r - 16, exey);
    ctx.fillText("E", exey.ex, exey.ey);
    _j(180 + 3, 0, center_w, center_h, r - 16, exey);
    ctx.fillText("S", exey.ex, exey.ey);
    _j(270 + 3, 0, center_w, center_h, r - 16, exey);
    ctx.fillText("W", exey.ex, exey.ey);
    ctx.stroke();
    ctx.font = "16px sans-serif";
    ctx.textAlign = "end";
    ctx.fillStyle = "cyan";
    ctx.fillText(_d('call').value + '-' + _d('grid').value, c.width - 10, c.height - 32);
    ctx.font = "20px sans-serif";
    ctx.textAlign = "left";
    ctx.fillStyle = "white";
    ctx.fillText("©CSN Technologies S.A.T.", c.width - 260, c.height - 5);
    if (!data) return;
    if (gsatsD) {
        top = legendTop - 10
        l = legendLeft - 5;
        ctx.textAlign = "left";
        ctx.font = "24px sans-serif";
        ctx.fillStyle = "white";
        ctx.fillText('GPS Satellites', center_w + r + l, top);
        top += 20;
        ctx.font = "12px sans-serif";
        bleft = center_w + r + l + 30;
        bw = 160;
        gsats.gps.forEach(s => {
            if (s[0]) {
                _j(s[1], s[2], center_w, center_h, r, exey);
                ctx.strokeStyle = "white";
                ctx.fillStyle = s[3] < 1 ? "red" : "green";
                if (s[3] < 1) ctx.fillStyle = "red";
                dot(ctx, exey.ex, exey.ey, markerSize * 1.5);
                ctx.strokeStyle = ctx.fillStyle = "white";
                ctx.fillText(s[0], exey.ex - 7, exey.ey + 5);
                ctx.fillText(s[0], center_w + r + l, top);
                if (ldata.gpslock) ctx.fillText(ldata.gpslat.toFixed(5) + ', ' + ldata.gpslon.toFixed(5), center_w + r + l, c.height - 30);
                ctx.fillStyle = s[3] < 1 ? "red" : "green";
                ctx.strokeRect(bleft, top - 13, bw, 14);
                ctx.fillRect(bleft + 1, top - 11, (bw * (s[3] / 99.0)) - 2, 10);
                top += 18;
            }
        });
        return;
    }
    var left = legendLeft;
    var top = legendTop;
    var aaz = data.az;
    var ael = data.el;
    if (data.flipped == 1) {
        aaz = flipAZ(aaz);
        ael = _k1(ael);
    }
    _j(aaz, ael, center_w, center_h, r, exey);
    ctx.fillStyle = "transparent";
    if (data.flipped == 1) {
        ctx.strokeStyle = "#ff33cc";
        ctx.fillStyle = "#ff33cc";
    } else {
        ctx.strokeStyle = "#ff6600";
        ctx.fillStyle = "#ff6600";
    }
    ctx.fillRect(exey.ex - markerSize, exey.ey - markerSize, markerSize * 2, markerSize * 2);
    top += 30;
    ctx.fillRect(center_w + r + left - markerSize, top - markerSize, markerSize * 2, markerSize * 2);
    ctx.textAlign = "left";
    ctx.fillStyle = "yellow";
    ctx.fillText("Antenna", center_w + r + left + 12, top + 7);
    if (data.mode != 1) return;
    if (!satPath) {
        _h3();
    }
    if (satPath instanceof Object) {
        ctx.lineWidth = 2;
        var pt;
        pt = satPath.path[0];
        _j(pt[0], pt[1], center_w, center_h, r, exey);
        for (pt of satPath.path) {
            if (pt[0] >= 0) {
                ctx.beginPath();
                if (pt[3]) ctx.strokeStyle = "lime";
                else ctx.strokeStyle = "yellow";
                ctx.moveTo(exey.ex, exey.ey);
                _j(pt[0], pt[1], center_w, center_h, r, exey);
                ctx.lineTo(exey.ex, exey.ey);
                ctx.stroke();
            }
        }
        ctx.lineWidth = 1;
    }
    if (data.mode == 1) {
        _j(data.aosAZ, 0, center_w, center_h, r, exey);
        ctx.fillStyle = "lime";
        ctx.strokeStyle = "black";
        dot(ctx, exey.ex, exey.ey, markerSize);
        top += 30;
        dot(ctx, center_w + r + left, top, markerSize);
        ctx.textAlign = "left";
        ctx.fillStyle = "yellow";
        ctx.fillText("AOS", center_w + r + left + 12, top + 7);
        _j(data.losAZ, 0, center_w, center_h, r, exey);
        ctx.fillStyle = "red";
        ctx.strokeStyle = "black";
        dot(ctx, exey.ex, exey.ey, markerSize);
        top += 30;
        dot(ctx, center_w + r + left, top, markerSize);
        ctx.textAlign = "left";
        ctx.fillStyle = "yellow";
        ctx.fillText("LOS", center_w + r + left + 12, top + 7);
    }
    ctx.textAlign = "left";
    ctx.fillStyle = "black";
    if (data.satEL < 0.0) {
        ctx.strokeStyle = "red";
        var c = -(data.satEL / 30.0);
        ctx.fillStyle = hslToHex(1, 0.3, 1 - c);
    } else {
        ctx.fillStyle = "white";
        ctx.strokeStyle = "black";
    }
    _j(data.satAZ, data.satEL, center_w, center_h, r, exey);
    _j1(ctx, exey.ex, exey.ey, markerSize);
    top += 30;
    _j1(ctx, center_w + r + left, top, markerSize);
    ctx.textAlign = "left";
    ctx.fillStyle = "yellow";
    ctx.fillText("Satellite", center_w + r + left + 12, top + 7);
    ctx.font = "12px 'IBM3270'";
    ctx.fillStyle = "white";
    ctx.textAlign = "left";
    ctx.fillText("dAZ " + (data.satAZ - aaz).toFixed(1), w - 70, 10);
    ctx.fillText("dEL " + (data.satEL - ael).toFixed(1), w - 70, 24);
}

function dot(ctx, x, y, r) {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
}

function getLog() {
    var url = '/jsonlog';
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Get Log";
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                qsolog = JSON.parse(this.responseText);
                _p(qsolog);
                windows.forEach(passData);
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function getSatLog() {
    var url = '/satlog';
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Get Log";
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                satlog = JSON.parse(this.responseText);
                _o(satlog);
                windows.forEach(passData);
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function getSched(popsatlist) {
    var url = '/sched';
    var xhttp = new XMLHttpRequest();
    pauseUpdates = "Pause-Get Sched";
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                _m(JSON.parse(this.responseText));
                windows.forEach(passData);
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
    if (!popsatlist) return;
    if (!satList) {
        var url = '/viewtle';
        var xhttp = new XMLHttpRequest();
        pauseUpdates = 'Pause-getSched';
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                pauseUpdates = '';
                try {
                    var data = JSON.parse(this.responseText);
                    if (data) {
                        data.sats = data.sats.sort(cmpA);
                    }
                    satList = data;
                    _k();
                } catch (e) {
                    return;
                }
            }
        }
        xhttp.open("GET", url, true);
        xhttp.send();
    } else {
        _k();
    }
}

function _g4() {
    var select = _d('schedsats');
    var catid = select.options[select.selectedIndex].value;
    select = _d('schedtrans');
    var freqid = select.options[select.selectedIndex].value;
    _f1(`B|S|${catid}|${freqid}`);
    setTimeout(function() {
        getSched(0);
    }, 500);
}

function _f4() {
    var select = _d('schedsats');
    var catid = select.options[select.selectedIndex].value;
    select = _d('schedtrans');
    for (i = select.options.length - 1; i >= 0; i--) {
        select.remove(i);
    }
    if (catid <= 0) return;
    var url = '/gettrans?b=' + catid;
    var xhttp = new XMLHttpRequest();
    pauseUpdates = 'Pause-getTransponders';
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            pauseUpdates = '';
            try {
                var data = JSON.parse(this.responseText);
                data.f.forEach(s => {
                    if (s[0] > 0) {
                        o = new Option(s[1], s[0], false, false);
                        select.add(o);
                    }
                });
                if (data.f.length < 2) select.add(new Option("None Found", -1, false, false));
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function _k() {
    var select = _d('schedsats');
    for (i = select.options.length - 1; i >= 0; i--) {
        select.remove(i);
    }
    let o = new Option("Choose Satellite", 0, false, false);
    select.add(o);
    satList.sats.forEach(s => {
        if (s.Name.length > 1) {
            z = new Option(s.Name, s.ID, false, false);
            select.add(z);
        }
    });
}

function _l(a, b) {
    return a[0] - b[0];
}

function _m(log) {
    let m = _d('divschedentries');
    m.innerHTML = '';
    if (log.log) {
        log.log = log.log.sort(_l);
    }
    console.log(log);
    let c = 0
    log.log.forEach(s => {
        if (s[1]) {
            c++;
            let d = ce("div");
            d.classList.add("row");
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = s[2];
            e.innerHTML += ` <span style='color: red; font-weight:900;cursor:pointer; title='Delete Log Entry' onclick="_r2(${s[1]});"'>X</span>`;
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = s[4];
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            if (s[0] > 0) {
                e.innerHTML = _n1(s[0]);
                e.innerHTML = e.innerHTML.replace(',', '<br>');
            } else {
                if (ldata.mode == 1 && ldata.catno == s[1]) {
                    e.innerHTML = 'TRACKING';
                    e.style = 'color: lime';
                } else {
                    e.innerHTML = 'PLEASE<br>WAIT';
                }
            }
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = s[5];
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = _n1(s[7]);
            e.innerHTML = e.innerHTML.replace(',', '<br>');
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = s[6];
            d.appendChild(e);
            m.appendChild(d);
        }
    });
}

function _n(a, b) {
    return a[4] - b[4];
}

function _o(log) {
    let m = _d('divsatlogentries');
    m.innerHTML = '';
    if (log.log) {
        log.log = log.log.sort(_n);
    }
    let c = 0
    log.log.forEach(s => {
        if (s[0]) {
            c++;
            let d = ce("div");
            d.classList.add("row");
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = s[0];
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = s[1];
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = _n1(s[4]);
            e.innerHTML = e.innerHTML.replace(',', '<br>');
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = s[2];
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = _n1(s[5]);
            e.innerHTML = e.innerHTML.replace(',', '<br>');
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = s[3];
            d.appendChild(e);
            m.appendChild(d);
        }
    });
}

function _p(log) {
    let m = _d('divlogentries');
    m.innerHTML = '';
    let c = 0
    log.log.forEach(s => {
        if (s[0]) {
            c++;
            let d = ce("div");
            d.classList.add("row");
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s1");
            e.classList.add("label");
            e.innerHTML = c;
            e.innerHTML += ` <span style='color: red; font-weight:900;cursor:pointer; title='Delete Log Entry' onclick="_q2(${s[9]});"'>X</span>`;
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.style = 'font-size: 0.7em';
            e.innerHTML = _n1(s[0]);
            e.innerHTML = e.innerHTML.replace(',', '<br>');
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = s[1] + "&nbsp;";
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            if (s[2]) {
                a = ce("a");
                a.setAttribute('href', `https://www.qrz.com/lookup?tquery=${s[2]}`);
                a.setAttribute('target', '_qrz' + c);
                a.innerHTML = s[2];
                e.appendChild(a);
            } else {
                e.innerHTML = "&nbsp;";
            }
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            if (s[3]) {
                a = ce("a");
                a.setAttribute('href', `https://www.levinecentral.com/ham/grid_square.php?Grid=${s[3]}`);
                a.setAttribute('target', '_grid' + c);
                a.innerHTML = s[3] + "&nbsp;";
                e.appendChild(a);
            } else {
                e.innerHTML = "&nbsp;";
            }
            d.appendChild(e);
            e = ce("div");
            e.classList.add("col");
            e.classList.add("s2");
            e.classList.add("label");
            e.innerHTML = s[8] + "&nbsp;";
            d.appendChild(e);
            m.appendChild(d);
        }
    });
}

function _r(s) {
    s = parseInt(s);
    m = Math.floor(s / 60);
    s = s % 60;
    return m.toString().padStart(2, '0') + ':' + s.toString().padStart(2, '0');
}

function _q() {
    var x;
    freqList = 0;
    var m = _d('cradio');
    _d('freqactivename').innerHTML = '---';
    _d('freqactivefreq').innerHTML = '--- / ---';
    _d('freqactivedop').innerHTML = '--- / ---';
    m.innerHTML = '';
    for (x = 1; x <= freqRows; x++) {
        var d = ce("div");
        d.classList.add("row");
        d.classList.add("border-bottom");
        d.style.display = 'none';
        d.id = 'freqrow' + x;
        e = ce("div");
        e.id = 'raddescr' + x;
        e.value = x;
        e.classList.add('t-bl');
        e.style.cursor = 'pointer';
        e.classList.add("col");
        e.classList.add("s4");
        e.classList.add("label");
        e.classList.add("w3-t-bl");
        d.appendChild(e);
        clk1 = e;
        e = ce("div");
        e.id = 'radup' + x;
        e.classList.add("col");
        e.classList.add("s4");
        e.classList.add("label");
        e.classList.add("w3-t-y");
        d.appendChild(e);
        e = ce("div");
        e.id = 'raddown' + x;
        e.classList.add("col");
        e.classList.add("s4");
        e.classList.add("label");
        e.classList.add("w3-t-y");
        d.appendChild(e);
        m.appendChild(d);
        clk1.addEventListener('click', function(event) {
            _s(this.value);
        });
    }
}

function _s(p) {
    _f1('A|' + p);
    _d('sstat').value = -1;
    _d('message').innerHTML = '';
    _d('freqrow' + (ldata.afreq + 1)).style.backgroundColor = 'transparent';
    _d('freqrow' + (p + 1)).style.backgroundColor = '#616161';
    _d('PL').value = '0';
    setTimeout(function() {
        _g1(false);
    }, 200);
}

function _t(vfo, e) {
    var mode = e.value;
    var data = '0';
    if (mode >= 100) {
        mode -= 100;
        data = '1';
    }
    _f1('m|' + vfo + "|" + mode + "|" + data);
}

function _u(e) {
    _f1('w|' + e.options[e.selectedIndex].value);
}

function _v(e) {
    _f1('h|' + e.options[e.selectedIndex].value);
}

function _w(e) {
    _f1('Z|B|' + e.options[e.selectedIndex].value);
}

function _x(e) {
    _f1('h|' + e.options[e.selectedIndex].value);
}

function _y(e) {
    e.stopPropagation();
    e.preventDefault();
    _f1('r');
    setTimeout(function() {
        _g1(false);
    }, 100);
}
var windows = [];
var windowidx = 0;

function openWindow(q = '') {
    w = window.open('/win?q=' + q, 'child2' + windowidx, "width=1024,height=950");
    windows.push(w);
    windowidx++;
    if (qs == 0) h1_(0);
    setTimeout(function() {
        _j2();
    }, 2000);
}

function passData(item, index, arr) {
    ldata.satPath = satPath;
    ldata.qsolog = qsolog;
    ldata.mycall = _d('call').value;
    ldata.mygrid = _d('grid').value;
    ldata.groundTrack = groundTrack;
    ldata.predictList = predictList;
    ldata.timef = _d('timef').value;
    ldata.mine = parseFloat(_d('minpass').value);
    item.postMessage(ldata, "*");
}

function _z(pdata) {
    if (pdata.cmd == 'clearqsolog') qsolog = 0;
    if (pdata.cmd == 'track') {
        _d4(pdata.name, pdata.catno, pdata.aost);
    }
    if (pdata.cmd == 'future') {
        predictList = 0;
        lastPredict = 0;
        _i1(false);
    }
    if (pdata.cmd == 'lookup') lookup(pdata.call);
    if (pdata.cmd == 'loglogin') {}
}

function gxde(d, e) {
    try {
        return d.getElementsByTagName(e)[0].childNodes[0].nodeValue;
    } catch (e) {
        return '';
    }
    return '';
}

function pxml(t) {
    const p = new DOMParser();
    return p.parseFromString(t, "application/xml");
}

function lookup(c, page = 0) {
    if (c) _d("logCallsign").value = c;
    else c = _d("logCallsign").value;
    if (_d("qrzl").value.length > 1) {
        doLookup = 1;
        lastLookupTime = new Date().getTime() / 1000;
        c = c.split('/')[0];
        url = "https://xmldata.qrz.com/xml/current/?s=" + qs + ";callsign=" + c;
        _d1(url, _a1)
    } else {
        doLookup = 0;
        alert('ERROR: QRZ Not Setup');
    }
    if (page) {
        window.event.preventDefault();
        window.open('https://www.qrz.com/lookup?tquery=' + c, '_qrz');
    }
}

function _a1(v) {
    n = _d('logGridsquare');
    n.value = '';
    n.focus();
    d = pxml(v);
    e = gxde(d, 'Error');
    if (e.length > 2) {
        console.log('QRZ ERR');
        h1_(0);
        return;
    }
    doLookup = 0;
    lastqrz = d;
    v = gxde(d, 'fname') + ' ' + gxde(d, 'name');
    if (v.length > 1) _d('logCallname').value = v;
    _d("logGridsquare").value = gxde(d, 'grid');
    _d('logst').value = gxde(d, 'state');
    _d('logcntry').value = gxde(d, 'country');
    var f = new FormData(_d('frmc'));
    ldata.call = Object.fromEntries(f.entries());
    windows.forEach(passData);
}

function _d1(url, fn) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            try {
                console.log("Gencall", this.responseText);
                fn(this.responseText);
            } catch (e) {
                return;
            }
        }
    }
    xhttp.open("GET", url, true);
    xhttp.send();
}

function h1_(v) {
    console.log('h1_', v);
    if (v == 0) {
        qs = 0;
        if (_d("qrzl").value.length < 1) return;
        pass = _d("qrzp").value;
        pass = pass.replace(/#/g, "%23");
        url = "https://xmldata.qrz.com/xml/current/?username=" + _d("qrzl").value + ";password=" + pass; //+"&agent=CSN_SAT";
        _d1(url, h1_);
    } else {
        d = pxml(v);
        e = gxde(d, 'Error');
        if (e.length > 1) {
            _d('message').innerHTML = "QRZ: " + e;
            return;
        } else {
            qs = gxde(d, 'Key');
            if (doLookup) {
                lookup(_d("logCallsign").value);
            }
        }
        doLookup = 0;
    }
}

function _b1() {
    var tnow = new Date().getTime() / 1000;
    if (tnow - lastW < 15 * 60) return;
    if (!_d('wkey').value) return;
    lastW = tnow;
    url = "https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + _d('wkey').value;
    _d1(url, _c1);
}

function _c1(d) {
    d = JSON.parse(d);
    t = d.main.temp - 273.15;
    s = d.wind.speed * 3.6;
    g = (d.wind.gust || 0) * 3.6;
    slab = 'Km/h';
    tlab = 'C';
    if (_d('lcdunits').value == 1) {
        t = t * (9.0 / 5.0) + 32;
        tlab = 'F';
        s = s * 0.622;
        g = g * 0.621;
        slab = 'mph'
    }
    if (g) g = 'G' + g.toFixed(1);
    else g = '';
    s = Math.round(s);
    t = Math.round(t);
    r = _d('wind');
    _d('wrow').style = 'display:block';
    r.innerHTML = `${d.wind.deg}&deg; @ ${s} ${slab} ${g}`;
    tm = new Date().toLocaleTimeString();
    sr = new Date(d.sys.sunrise * 1000).toLocaleTimeString();
    ss = new Date(d.sys.sunset * 1000).toLocaleTimeString();
    r.setAttribute('title', `Temp: ${t}${tlab}\n${d.weather[0].main}-${d.weather[0].description}\nSunrise: ${sr}\nSunset: ${ss}\nUpdated: ${tm}`);
}

function _e1() {
    return ['iPad Simulator', 'iPhone Simulator', 'iPod Simulator', 'iPad', 'iPhone', 'iPod'].includes(navigator.platform) || (navigator.userAgent.includes("Mac") && "ontouchend" in document)
}