var express = require('express');
var publicApi = express();
var privateApi = express();
var bodyParser = require('body-parser');
var fingerprint = require('./fingerprint.js');
var request = require('request');

const publicPort = 8001;
const privatePort = 8002;

var state = "Register";//"Normal";

//Process JSON
publicApi.use(bodyParser.json());
privateApi.use(bodyParser.json());

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
privateApi.post('/state', function(req, res) {
	//TODO set state here
});
privateApi.post('/users/add', function(req, res) {
	//TODO add a new user after registration
});


/** LISTEN **/

publicApi.listen(publicPort, function () {
  console.log('Public API listening on port ' + publicPort);
});

privateApi.listen(privatePort, function() {
  console.log('Private API listening on port ' + privatePort);
});
