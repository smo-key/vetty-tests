module.exports = function (Schema, mongoose) {

  var loginSchema = new Schema({
    id: {
      type: Number,
      get: v => Math.round(v),
      set: v => Math.round(v),
      min: 0,
      max: 200,
      required: [true, "Fingerprint ID is required"],
      unique: true
    },
    registerDate: {
      type: Date,
      validate: {
        validator: (y) => { return y > new Date(2016, 1, 1)},
        message: "Register date is invalid"
      }
    },
    date: {
      type: Date,
      validate: {
        validator: (y) => { return y > new Date(2016, 1, 1)},
        message: "Date is invalid"
      }
    },
    hours: {
      type: Number,
      default: 0
    }
  });

  loginSchema.index({ id: 1, registerDate: 1, date: 1 });

  return mongoose.model('Login', loginSchema);
}
