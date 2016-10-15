var express = require('express');
var publicApi = express();
var privateApi = express();
var bodyParser = require('body-parser');
var request = require('request');
var assert = require('assert');
var colors = require('colors');

var _fp = { }
_fp.fp = require('./fingerprint.js');

const publicPort = 8001;
const privatePort = 8002;

//Process JSON
publicApi.use(bodyParser.json());
privateApi.use(bodyParser.json());

/** FINGERPRINT **/
_fp.fp.init();

/** DATABASE **/
var mongoose = require('mongoose');
mongoose.Promise = require('q').Promise;
mongoose.connect("mongodb://localhost:27017/vetty", { config: { autoIndex: false } });

//Load schema
var Schema = mongoose.Schema;
    User = require('./db/user.js')(Schema, mongoose);

//Connect to database
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'Connection error: '));

db.once('open', () => {
	console.log("Connected to database on port 27017");
});

/** PUBLIC (END-USER) API **/

publicApi.post('/api/users/delete', function(req, res) {
	var userId = req.body.userId;
	var fpId = req.body.fpId;
	var adminToken = req.body.token;

	//TODO make sure to delete from fingerprint sensor
});

publicApi.post('/api/users/list', function(req, res) {
	var adminToken = req.body.token;
});

/** PRIVATE (PYTHON) API - called from Python server **/

privateApi.post('/login', function(req, res) {
	var fpId = req.body.fpId;

	_fp.fp.identify().then((id) => {
		res.send("OK " + id);
	}, (err) => {
		res.send(_fp.fp.getError(err));
	});

	//TODO Respond with successful?, message, out?, timeIn, timeOut, hours, name, userId
});

privateApi.get('/pressed', function(req, res) {
	_fp.fp.ispressed().then((pressed) => {
		res.send(pressed ? "True" : "False");
	}, (err) => {
		res.send(_fp.fp.getError(err));
	});
});

privateApi.get('/state', function(req, res) {
	res.send(state);
});

privateApi.post('/wait/release', function(req, res) {
	//Wait for finger to release
	_fp.fp.waitRelease().then(() => {
		res.send("OK");
	}, (err) => {
		res.send(_fp.fp.getError(err));
	});
});
privateApi.post('/led/off', function(req, res) {
	_fp.fp.ledoff().then(() => {
		res.send("OK");
	}, (err) => {
		res.send(_fp.fp.getError(err));
	});
});
privateApi.post('/register/1', function(req, res) {
	//TODO get next fpId
	var fpId = 0;

	_fp.fp.enroll1(fpId).then(() => {
		console.log("Register phase 1 complete")
		res.send("OK " + fpId)
	}, (err) => {
		res.send(_fp.fp.getError(err));
	});
});
privateApi.post('/register/2', function(req, res) {
	_fp.fp.enroll2().then(() => {
        console.log("Register phase 2 complete")
        res.send("OK")
    }, (err) => {
        res.send(_fp.fp.getError(err));
    });
});

privateApi.post('/register/3', function(req, res) {
	_fp.fp.enroll3().then(() => {
	    console.log("Register phase 3 complete")
		//res.send("OK");

		//Add row to database
		var user = {
			firstName: req.body.firstName,
			lastName: req.body.lastName,
			id: req.body.fpId,
			studentId: req.body.studentId,
			registerDate: Date.now(),
			logins: [ ],
			totalHours: 0
		};
		console.log(user)

		var predicate = { id: req.body.fpId };
		
		//update prevents duplicates and allows overwrite
		User.findOneAndUpdate(predicate, user, { new: true, upsert: true, runValidators: true }, (err, newRecord) => {
			console.log("Enroll new user".yellow);
			console.log(newRecord);
			if (err) {
				Object.keys(err.errors).forEach(function(error, key, _array) {
					console.error("Validation error: " + err.errors[error].message + " on field '" + error + "'");
				});
			}
			res.send("OK");
		});
  }, (err) => {
      res.send(_fp.fp.getError(err));
  });
});


/** LISTEN **/

publicApi.listen(publicPort, function () {
  console.log('Public API listening on port ' + publicPort);
});

privateApi.listen(privatePort, function() {
  console.log('Private API listening on port ' + privatePort);
});
