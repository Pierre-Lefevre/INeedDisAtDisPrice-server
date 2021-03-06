const mongoose = require('mongoose')

let Schema = mongoose.Schema

const usersSchema = new Schema({
  id_user: String,
  id_product: String,
  price: Number,
  done: {type: Boolean, default: false},
  product: Object
}, {
  strict: false,
  versionKey: false
})

const Alerts = mongoose.model('alerts', usersSchema)

module.exports = Alerts
