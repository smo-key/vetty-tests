var express = require('express');
var publicApi = express();
var privateApi = express();
var bodyParser = require('body-parser');
var fingerprint = require('./fingerprint.js');

const publicPort = 8001;
const privatePort = 8002;

//Process JSON
publicApi.use(bodyParser.json());
privateApi.use(bodyParser.json());

/** PUBLIC (END-USER) API **/

publicApi.post('/api/users/register', function(req, res) {
	var firstName = req.body.firstName;
	var lastName = req.body.lastName;
	var userId = req.body.userId;
	var adminToken = req.body.token;
	
	//TODO send display commands to Python server (8003) when starting and updating
	//Do not exit register mode until command is given
	//Users enter their info via keyboard
});

publicApi.post('/api/users/registerEnd', function(req, res) {
	var adminToken = req.body.token;

	//TODO End registration mode
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

privateApi.post('/fp/login', function(req, res) {
	var fpId = req.body.fpId;
	
	//TODO Respond with successful?, message, out?, timeIn, timeOut, hours, name, userId
});


/** LISTEN **/

publicApi.listen(publicPort, function () {
  console.log('Public API listening on port ' + publicPort);
});

privateApi.listen(privatePort, function() {
  console.log('Private API listening on port ' + privatePort);
});
