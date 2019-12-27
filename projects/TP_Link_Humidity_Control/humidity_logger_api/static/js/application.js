
$(document).ready(function(){
    //connect to the socket server.
    // var serverHost = '//' + document.domain + ':' + location.port;
    var serverHost = 'https://rpi-home-weather-station.herokuapp.com';

    var socket = io.connect(serverHost + '/io-humidity');
    //receive details from server
    socket.on('humidity', function(msg) {
        console.log("humidity number");
        console.log(msg);
        $('#humidity').html(`Current Humidity ${msg.humidity} @ ${msg.time}`);
    });

    //connect to the socket server.
    var socket_temprature = io.connect(serverHost+ '/io-temprature');
    var numbers_received = [];
    //receive details from server
    socket_temprature.on('temprature', function(msg) {
        console.log("temprature number");
        console.log(msg);
        $('#temprature').html(`Current Temprature ${msg.temprature} @ ${msg.time}`);
    });

});