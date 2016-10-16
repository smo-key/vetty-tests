var express = require('express');
var publicApi = express();
var privateApi = express();
var bodyParser = require('body-parser');
var request = require('request');
var assert = require('assert');
var colors = require('colors');
var moment = require('moment');

var _fp = { }
_fp.fp = require('./fingerprint.js');

const publicPort = 8001;
const privatePort = 8002;

//Process JSON
publicApi.use(bodyParser.json());
privateApi.use(bodyParser.json());

/** UTIL **/
Number.prototype.toFixedDown = function(digits) {
    var re = new RegExp("(\\d+\\.\\d{" + digits + "})(\\d)"),
        m = this.toString().match(re);
    return m ? parseFloat(m[1]) : this.valueOf();
};

/** FINGERPRINT **/
_fp.fp.init();

/** DATABASE **/
var mongoose = require('mongoose');
mongoose.Promise = require('q').Promise;
mongoose.connect("mongodb://localhost:27017/vetty", { config: { autoIndex: false } });

//Load schema
var Schema = mongoose.Schema;
    User = require('./db/user.js')(Schema, mongoose);
	Login = require('./db/login.js')(Schema, mongoose);

//Connect to database
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'Connection error: '));

db.once('open', () => {
	console.log("Connected to database on port 27017");
});

/** PUBLIC (END-USER) API **/

publicApi.post('/api/users/delete', function(req, res) {
	var userId = req.body.userId;

  

	//TODO make sure to delete from fingerprint sensor
});

publicApi.get('/api/users/list', function(req, res) {
	res.header('Access-Control-Allow-Origin', 'http://10.42.0.231:5000');
	User.find({}).sort({ id: 1 }).exec((err, users) => {
		for (var i=0; i<users.length; i++)
		{
			users[i].totalHours = users[i].totalHours.toFixedDown(1);
		}
		console.log(users);
		res.send(users);
	});
});

publicApi.post('/api/settings/deleteall', function(req, res) {
	_fp.fp.deleteAll().then(() => {
		console.log("All fingerprints deleted!");
		res.send({ ok: true });
	});
	User.remove({}, function(err, data) {
        console.log(data);
    });
    Login.remove({}, function(err, data) {
        console.log(data);
    });
});

/** PRIVATE (PYTHON) API - called from Python server **/

privateApi.post('/login', function(req, res) {
	_fp.fp.identify().then((id) => {

		var user = { };
		user.ok = true;

		User.findOne({id: id}, function(err, dbuser) {
			if (err) { console.error(err); }
			console.log(dbuser);
			user.firstName = dbuser.firstName;
			user.lastName = dbuser.lastName;
			user.id = id.toString();
			user.studentId = dbuser.studentId;

			//Get last entry and exit today -> lastLogin
      		var now = new Date();
      		var truncDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
			console.log(now);
			console.log(truncDate);
			Login.find({ id: id, registerDate: dbuser.registerDate, date: truncDate })
			.sort({dateTime: -1})
			.limit(2)
			.exec((err, entries) => {
        		if (err) { throw err; }
				//entries will either contain [ exit, entry ], [ entry, entry ], [entry], or [ ]

				 console.log("Get last entry and exit today".yellow);
       			 console.log(entries);

        var login;
        var totalHours;
        if (entries.length > 0)
        {
          //Create new login record - set all properties
    			//If latest item was an entry, set hours to the difference between the two
    			//If latest item was an entry, add to user's total hours -> hoursTotal
          var latestItemWasEntry = entries[0].isEntry;
		  var ms_per_hour = 1000 * 60 * 60;
          var differenceBetweenLast = (now - entries[0].dateTime) / ms_per_hour;
		  var newHours = latestItemWasEntry ? differenceBetweenLast : 0;
          login = {
            id: id,
            registerDate: dbuser.registerDate,
            date: truncDate,
            dateTime: now,
            isEntry: !latestItemWasEntry, //if exit, entry - if entry, exit
            hours: newHours
          }
          user.isLeaving = latestItemWasEntry;
          totalHours = dbuser.totalHours + newHours;
        }
        else {
          login = {
            id: id,
            registerDate: dbuser.registerDate,
            date: truncDate,
            dateTime: now,
            isEntry: true,
            hours: 0
          }
          user.isLeaving = false;
          totalHours = dbuser.totalHours;
        }

        console.log(totalHours);
        user.hoursTotal = totalHours.toFixedDown(1).toString();
        console.log(login);

		//Update user with new totalHours
		User.findByIdAndUpdate(dbuser._id, { totalHours: totalHours }, { new: true }, (err, newUser) => {
			console.log("User updated with new totalHours".yellow);
			console.log(newUser);
		});

        //Get last entry
        Login.find({ id: id, registerDate: dbuser.registerDate, isEntry: true })
        .sort({dateTime: -1}).limit(1).exec((err, entries) => {
          if (err) { throw err; }

		  console.log("Get last entry".yellow);
		  var lastEntry = entries[0];
		  console.log(lastEntry);

		  if (entries.length > 0)
		  {

          //TODO convert lastEntry to pretty time
          user.lastEntry = moment(lastEntry.dateTime).calendar();

		  } else
          {
			user.lastEntry = "";
		  }

          //Push new login record to login table
          Login.findOneAndUpdate({ id: id, registerDate: dbuser.registerDate, date: truncDate, dateTime: now },
			login , { upsert: true, new: true, runValidators: true }, (err, newLogin) => {
			if (err) { throw err; }
			console.log("New login entry saved".yellow)
			console.log(newLogin);
		  });

            //Sum hours of all logins that occured today, including the new one -> hoursToday
      			Login.find({id: id, registerDate: dbuser.registerDate, date: truncDate, isEntry: false}, (err, logins) => {
              console.log("Get all exits today".yellow);
			  console.log(logins);
			  //All exits today
			  var hoursToday;
			  if (lastEntry)
              { hoursToday = lastEntry.hours; }
			  else { hoursToday = 0; }

              for (var i=0; i<logins.length; i++) {
               	hoursToday = hoursToday + logins[i].hours;
              }

			  setTimeout(() => {

				var minutesToday = hoursToday * 60;
				var hoursTodayString = Math.floor(hoursToday).toString() + ":" + ((minutesToday % 60) < 10 ? "0" : "")
				 + Math.floor(minutesToday % 60).toString()
				user.hoursToday = hoursTodayString;

				console.log("Return user".yellow);
				console.log(user);
				res.send(user);
			  }, 100);
            }); //login.find
        }); //login.find
			});
		});

		//res.send("OK " + id);
	}, (err) => {
		res.send({ ok: false, error: _fp.fp.getError(err)});
	});

	//TODO respond with OK if successful then id, firstName, lastName, hoursToday,
	//hoursTotal, lastEntry, and isLeaving
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
	//Get next available fpId
	User.find({}).sort({id: 1}).exec(function(err, users) {
		var fpId = 0;
		console.log(users);
		for (var i=0; i<users.length; i++) {
			if (users[i].id == fpId) {
				fpId++;
			} else { break; }
		};

		console.log(fpId);
		_fp.fp.enroll1(fpId).then(() => {
     		console.log("Register phase 1 complete")
        	res.send("OK " + (fpId))
    	}, (err) => {
    	    res.send(_fp.fp.getError(err));
	    });
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
