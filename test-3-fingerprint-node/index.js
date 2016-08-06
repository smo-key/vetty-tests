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
		
		deleteID(0)
		.then(function() { return enroll(0); })
		.then(function() {
			console.log("All done!");
		}, function(err) {
			console.error(fps.decodeError(err) + " (" + err + ")");
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

var deleteID = function(id) {
	return (new Promise(function(resolve, reject){
		var errorHandler = function(err) {
			console.log("Error resolved");
			resolve();
		}
		
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

      ledON()
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

/**
function enroll(id)
{
	console.log("Waiting for finger...");
	fps.waitFinger(15000).then(function() {
      		console.log("Finger now down");
		fps.enrollStart(0).then(function() {
			console.log("Enroll started!");
			fps.enroll1(id).then(function() {
				console.log("Enroll 1 complete!");
				fps.enroll2(id).then(function() {
                        		console.log("Enroll 2 complete!");
					fps.enroll3(id).then(function() {
						console.log("Enroll complete!");
                        		}, function(err) {
                                		console.error(fps.decodeError(err));
                        		});
				}, function(err) {
                        	        console.error(fps.decodeError(err));
                        	});
			}, function(err) {
				console.error(fps.decodeError(err));
			});
		}, function(err) {
			console.error(fps.decodeError(err));
		});
       	}, function(err) {
       	        console.error(err);
        });
}
**/
function test()
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
