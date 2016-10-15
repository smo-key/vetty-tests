module.exports = function (Schema, mongoose) {

  var userSchema = new Schema({
    firstName: {
      type: String,
      required: [ true, "First name is required"],
      validate: { validator: s => { return s.trim().length > 0 && !/[\[\]! ]/.test(s.trim()) }, message: "First name is invalid"},
      set: s => { return s.trim().charAt(0).toUpperCase() + s.trim().slice(1).toLowerCase() }
    },
    lastName: {
      type: String,
      required: [ true, "Last name is required"],
      validate: { validator: s => { return s.trim().length > 0 && !/[\[\]!]/.test(s.trim()) }, message: "Last name is invalid"},
      set: s => { return s.trim().charAt(0).toUpperCase() + s.trim().slice(1).toLowerCase() }
    },
    id: {
      type: Number,
      get: v => Math.round(v),
      set: v => Math.round(v),
      min: 0,
      max: 200,
      required: [true, "Fingerprint ID is required"],
      unique: true
    },
    studentId: {
      type: String
    },
    registerDate: {
      type: Date,
      validate: {
        validator: (y) => { return y > new Date(2016, 1, 1)},
        message: "Register date is invalid"
      }
    },
    logins: [{ type: Schema.Types.ObjectId, ref: "Login" }],
    totalHours: { type: Number, default: 0 }
  });
  userSchema.index({ id: 1 });
  
  return mongoose.model('User', userSchema);
};
