const mongoose = require('mongoose')

let Schema = mongoose.Schema

const usersSchema = new Schema({
  id_user: String,
  id_product: String,
  price: String,
  done: {type: Boolean, default: false}
}, {
  strict: false,
  versionKey: false
})

const Alerts = mongoose.model('alerts', usersSchema)

module.exports = Alerts
