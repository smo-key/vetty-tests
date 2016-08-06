var GT511C3 = require('gt511c3');

var fps = new GT511C3('/dev/ttyAMA0', { baudrate: 9600, debug: false });

fps.init().then(
    function() {
        //init ok
        console.log('Firmware version: ' + fps.firmwareVersion);
        console.log('Iso area max: ' + fps.isoAreaMaxSize);
        console.log('Device serial number: ' + fps.deviceSerialNumber);
	fps.ledONOFF(fps.LED_ON);
	fps.getEnrollCount().then(function(count) {
  		console.log("Enrolled fingerprints count: " + count);
		enroll();
	});
	//start();
    },
    function(err) {
        console.log('init err: ' + err);
    }
);

function enroll()
{
	//fps.ledONOFF(fps.LED_ON);
	fps.isPressFinger().then(function() {
		console.log("Finger is down");
		fps.ledONOFF(fps.LED_OFF);
	}, function(err) {
		if ((err === undefined) || (err == "finger is not pressed"))
			console.log("Finger not down");
		else 
			console.error(fps.decodeError(err));
		fps.ledONOFF(fps.LED_OFF);
	});
	/**fps.waitFinger(5000).then(function() {
		console.log("Finger pressed!");
		fps.waitReleaseFinger(10000).then(function() {
			console.log("Finger released!");
		}, function(err) {
			console.error(fps.decodeError(err));
		});
	}, function(err) {
		console.error(fps.decodeError(err));
	});**/
}

function start()
{
    fps.ledONOFF(fps.LED_OFF);
    while(!fps.isPressFinger()) { }
    fps.ledONOFF(fps.LED_OFF);
}
