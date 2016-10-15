var GT511C3 = require('gt511c3');
fps = new GT511C3('/dev/ttyAMA0', { baudrate: 115200, debug: false });

/** FINGERPRINT **/
fps.init().then(() => {
	console.log("Fingerprint sensor initialized!")
	fps.deleteAll().then(() => {
		console.log("All fingerprints deleted!");
	});
});

/** DATABASE **/
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
	User.remove({}, function(err, data) {
		console.log(data);
	});
});
