var GT511C3 = require('gt511c3');
fps = new GT511C3('/dev/ttyAMA0', { baudrate: 115200, debug: false });

exports.fps = function() { return fps; }

exports.init = function() {
	return(new Promise(function(resolve, reject) {
		fps.init().then(
		function() {
	        	//init ok
		        console.log('Firmware version: ' + fps.firmwareVersion);
	       		//console.log('Iso area max: ' + fps.isoAreaMaxSize);
		        console.log('Device serial number: ' + fps.deviceSerialNumber);
			fps.getEnrollCount().then(function(count) {
  				console.log("Enrolled fingerprints count: " + count);
			}).then(function() { fps.ledONOFF(0); }).then(function() {
				console.log("Init complete!")
			});
		}).then(function() { resolve(); });
	}));
}

function delay_ms(ms) {
    return (new Promise(function(resolve, reject) {
      setTimeout(resolve, ms);
    }));
}

exports.getError = function(code) {
	return fps.decodeError(code) + " (" + code + ")"
}

exports.identify = function() {
	return (new Promise(function(resolve, reject){
		fps.ledONOFF(1)
		//.then(function() { return fps.waitReleaseFinger(10000); })
		.then(function() { return fps.waitFinger(2000); })
		.then(function() { return fps.captureFinger(); })
		.then(function() { return fps.identify(); })
		.then(function(id) {
			console.log("Logged in as " + id);
			fps.ledONOFF(0).then(() => { resolve(id); });
			resolve(id);
		}, function(err) {
			fps.ledONOFF(0).then(() => { reject(err); });
		});
	}));
}

exports.ispressed = function() {
	return (new Promise(function(resolve, reject){
		fps.ledONOFF(1)
		.then(() => { return fps.isPressFinger(); })
		.then(() => { resolve(true); },
		      (err) => { resolve(false); });
	}));
}

exports.close = function() {
	return (new Promise(function(resolve, reject) {
		fps.closePort()
		.then(() => { resolve(); },
			  (err) => { reject(err); })	
	}));
}

exports.ledoff = function(id) {
    return (new Promise(function(resolve, reject){
        fps.ledONOFF(0).then(function() {
            resolve();
        }, function(err) {
            reject(err);
        });
    }));
}


exports.deleteID = function(id) {
	return (new Promise(function(resolve, reject){		
		fps.deleteID(id).then(function() {
			console.log("ID " + id + " Deleted!");
			resolve();
		}, function(err) {
			console.warn("No ID to delete at index " + id);
			resolve();
		});
	}));
}

exports.deleteAll = function() {
    return (new Promise(function(resolve, reject){
        fps.deleteAll().then(function() {
            console.log("All IDs deleted!");
            resolve();
        }, function(err) {
			console.log("No IDs to delete!");
            resolve();
        });
    }));
}

exports.enroll = function(ID) {
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

exports.enroll1 = function(id) {
    return (new Promise(function(resolve, reject) {
      var errorHandler = function(err) {
        reject(err);
      }
      var capture = function() {
        return fps.captureFinger(fps.BEST_IMAGE);
      };
      var waitFinger = function() {
        return fps.waitFinger(10000);
      };
      var ledON = function() {
        return fps.ledONOFF(1);
      }
      var ledOFF = function() {
        return fps.ledONOFF(0);
      }

      exports.deleteID(id)
        .then(ledON)
		.then(waitFinger)
        .then(() => { return fps.enrollStart(id); })
        .then(capture)
        .then(function() {
		  console.log("Enrolling ID " + id);
          return fps.enroll1();
        })
        .then(ledOFF)
      .then(function() {
        resolve();
      }, function(err) {
        ledOFF();
		//console.err("Enroll 1: " + exports.getError(err))
        reject(err);
      });
	}));
}

exports.enroll2 = function() {
    return (new Promise(function(resolve, reject) {
      var errorHandler = function(err) {
        reject(err);
      }
      var capture = function() {
        return fps.captureFinger(fps.BEST_IMAGE);
      };
      var waitFinger = function() {
        return fps.waitFinger(10000);
      };
      var ledON = function() {
        return fps.ledONOFF(1);
      }
      var ledOFF = function() {
        return fps.ledONOFF(0);
      }
      
	  ledON()
      	.then(waitFinger)
        .then(capture)
        .then(function() {
          return fps.enroll2();
        })
        .then(ledOFF)
      .then(function() {
        resolve();
      }, function(err) {
        ledOFF();
		//console.err("Enroll 2: " + exports.getError(err))
        reject(err);
      });
    }));
}

exports.enroll3 = function() {
    return (new Promise(function(resolve, reject) {
      var errorHandler = function(err) {
        reject(err);
      }
      var capture = function() {
        return fps.captureFinger(fps.BEST_IMAGE);
      };
      var waitFinger = function() {
        return fps.waitFinger(10000);
      };
      var ledON = function() {
        return fps.ledONOFF(1);
      }
      var ledOFF = function() {
        return fps.ledONOFF(0);
      }

      ledON()
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
		//console.err("Enroll 3: " + exports.getError(err))
        reject(err);
      });
    }));
}

exports.waitRelease = function() {
    return (new Promise(function(resolve, reject) {
      var errorHandler = function(err) {
        reject(err);
      }
      var capture = function() {
        return fps.captureFinger(fps.BEST_IMAGE);
      };
      var waitReleaseFinger = function() {
        return fps.waitReleaseFinger(10000);
      };
      var ledON = function() {
        return fps.ledONOFF(1);
	  }
      var ledOFF = function() {
        return fps.ledONOFF(0);
      }

	  ledON()
	  .then(waitReleaseFinger)
	  .then(ledOFF)
      .then(function() {
        resolve();
      }, function(err) {
        ledOFF();
        reject(err);
      });
    }));
}
