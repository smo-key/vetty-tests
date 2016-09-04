var express = require('express');
var publicApi = express();
var privateApi = express();
var bodyParser = require('body-parser');
var fp = require('./fingerprint.js');
var request = require('request');

const publicPort = 8001;
const privatePort = 8002;

var state = "Register";//"Normal or Register";

//Process JSON
publicApi.use(bodyParser.json());
privateApi.use(bodyParser.json());

/** FINGERPRINT **/
fp.init();

/** PUBLIC (END-USER) API **/

publicApi.post('/api/users/register', function(req, res) {
	//var firstName = req.body.firstName;
	//var lastName = req.body.lastName;
	//var userId = req.body.userId;
	var adminToken = req.body.token;
	
	//TODO send display commands to Python server (8003) when starting and updating
	//Do not exit register mode until command is given
	//Users enter their info via keyboard
	state = "Register"
	res.status(200).json({ });
});

publicApi.post('/api/users/registerEnd', function(req, res) {
	var adminToken = req.body.token;

	//TODO End registration mode
	state = "Normal";
	res.status(200).json({ });
});

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
	
	//TODO Respond with successful?, message, out?, timeIn, timeOut, hours, name, userId
});

privateApi.get('/state', function(req, res) {
	res.send(state);
});

/*
privateApi.post('/state', function(req, res) {
	//TODO set state here
});
*/

privateApi.post('/wait/release', function(req, res) {
	//Wait for finger to release
	fp.waitRelease().then(() => {
		console.log("Released!")
		res.send("OK");
	}, (err) => {
		res.send(fp.getError(err));
	});
});
privateApi.post('/led/off', function(req, res) {
	fp.ledoff().then(() => {
		res.send("OK");
	}, (err) => {
		res.send(fp.getError(err));
	});
});
privateApi.post('/reset', function(req, res) {
	fp.reset().then(() => {
		res.send("OK")
	}, (err) => {
		res.send(fp.getError(err));
	});
});
privateApi.post('/register/1', function(req, res) {
	fp.enroll1(2).then(() => {
		console.log("Register phase 1 complete")
		res.send("OK")
	}, (err) => {
		res.send(fp.getError(err));
	});
});
privateApi.post('/register/2', function(req, res) {
	fp.enroll2().then(() => {
        console.log("Register phase 2 complete")
        res.send("OK")
    }, (err) => {
        res.send(fp.getError(err));
    });
});
privateApi.post('/register/3', function(req, res) {
	fp.enroll3().then(() => {
        console.log("Register phase 3 complete")
        res.send("OK")
    }, (err) => {
        res.send(fp.getError(err));
    });
});


/** LISTEN **/

publicApi.listen(publicPort, function () {
  console.log('Public API listening on port ' + publicPort);
});

privateApi.listen(privatePort, function() {
  console.log('Private API listening on port ' + privatePort);
});
