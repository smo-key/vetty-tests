var GT511C3 = require('gt511c3');

var fps = new GT511C3('/dev/ttyAMA0', { baudrate: 9600, debug: true });

fps.init().then(
    function() {
        //init ok
        console.log('firmware version: ' + fps.firmwareVersion);
        console.log('iso area max: ' + fps.isoAreaMaxSize);
        console.log('device serial number: ' + fps.deviceSerialNumber);
	fps.ledONOFF(fps.LED_OFF);
    },
    function(err) {
        console.log('init err: ' + err);
    }
);

console.log("Ready!");
