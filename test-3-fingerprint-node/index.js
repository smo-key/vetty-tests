var GT511C3 = require('gt511c3');
var fps = new GT511C3('/dev/ttyAMA0', { baudrate: 9600, debug: false });

fps.init().then(
    function() {
        //init ok
        console.log('Firmware version: ' + fps.firmwareVersion);
        console.log('Iso area max: ' + fps.isoAreaMaxSize);
        console.log('Device serial number: ' + fps.deviceSerialNumber);
	fps.getEnrollCount().then(function(count) {
  		console.log("Enrolled fingerprints count: " + count);
		/*console.log("Starting enrollment...");
		enroll(1)
		.then(function() { console.log("Getting enroll count..."); return fps.getEnrollCount(); })
		.then(function(count) { return console.log("Enrolled fingerprints: " + count); })
		.then(function() { console.log("Starting identification..."); return identify(); })
		*/
		identify()
		.then(function() {
			console.log("All done!");
			fps.ledONOFF(0);
		}, function(err) {
			console.error(fps.decodeError(err) + " (" + err + ")");
			fps.ledONOFF(0);
		});
	});
    },
    function(err) {
        console.log('init err: ' + err);
    }
);

function delay_ms(ms) {
    return (new Promise(function(resolve, reject) {
      setTimeout(resolve, ms);
    }));
}

var identify = function() {
	return (new Promise(function(resolve, reject){
		fps.ledONOFF(1)
		.then(function() { return fps.waitReleaseFinger(10000); })
		.then(function() { return fps.waitFinger(10000); })
		.then(function() { return fps.captureFinger(); })
		.then(function() { return fps.identify(); })
		.then(function(id) {
			console.log("Logged in as " + id);
			fps.ledONOFF(0);
			resolve();
		}, function(err) {
			fps.ledONOFF(0);
			reject(err);
		});
	}));
}

var deleteID = function(id) {
	return (new Promise(function(resolve, reject){		
		fps.deleteID(id).then(function() {
			console.log("ID Deleted!");
			resolve();
		}, function(err) {
			console.warn("No ID to delete!");
			resolve();
		});
	}));
}

var enroll = function(ID) {
    return (new Promise(function(resolve, reject) {
      var errorHandler = function(err) {
        reject(err);
      }
      var start = function() {
        return fps.enrollStart(ID)
      }
      var capture = function() {
        return fps.captureFinger(fps.BEST_IMAGE);
      };
      var waitFinger = function() {
        return fps.waitFinger(10000);
      };
      var waitReleaseFinger = function() {
        return fps.waitReleaseFinger(10000);
      };
      var enroll_delay = function() {
        return delay_ms(500);
      }
      var blink_delay = function() {
        return delay_ms(100);
      }
      var ledON = function() {
        return fps.ledONOFF(1);
      }
      var ledOFF = function() {
        return fps.ledONOFF(0);
      }
      

      deleteID(ID)
        .then(ledON)
        .then(waitFinger)
        .then(start)
        .then(capture)
        .then(function() {
          return fps.enroll1();
        })
        .then(ledOFF)
        .then(blink_delay)
        .then(ledON)
        .then(waitReleaseFinger)

      .then(enroll_delay)

      .then(waitFinger)
        .then(capture)
        .then(function() {
          return fps.enroll2();
        })
        .then(ledOFF)
        .then(blink_delay)
        .then(ledON)
        .then(waitReleaseFinger)

      .then(enroll_delay)

      .then(waitFinger)
        .then(capture)
        .then(function() {
          return fps.enroll3();
        })
        .then(ledOFF)

      .then(function() {
        resolve();
      }, function(err) {
        ledOFF();
        reject(err);
      });
    }));
}
