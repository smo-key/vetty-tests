var express = require('express');
var publicApi = express();
var privateApi = express();
var bodyParser = require('body-parser');
var request = require('request');

var _fp = { }
_fp.fp = require('./fingerprint.js');

const publicPort = 8001;
const privatePort = 8002;

var state = "Normal";//"Normal or Register";

//Process JSON
publicApi.use(bodyParser.json());
privateApi.use(bodyParser.json());

/** FINGERPRINT **/
_fp.fp.init();

/** DATABASE **/
var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');

// Connection URL
var url = 'mongodb://localhost:27017/vetty';

// Use connect method to connect to the server
/*MongoClient.connect(url, function(err, db) {
  assert.equal(null, err);
  console.log("Connected successfully to server");
});*/

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

/*
privateApi.post('/state', function(req, res) {
	//TODO set state here
});
*/

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
	_fp.fp.enroll1(2).then(() => {
		console.log("Register phase 1 complete")
		res.send("OK")
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

addUser = function(data)
{
	
}

privateApi.post('/register/3', function(req, res) {
	console.log(req.body)
	_fp.fp.enroll3().then(() => {
        console.log("Register phase 3 complete")
        res.send("OK")
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
