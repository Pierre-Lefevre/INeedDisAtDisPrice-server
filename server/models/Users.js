const mongoose = require('mongoose')

let Schema = mongoose.Schema

const usersSchema = new Schema({
  firstname: String,
  lastname: String,
  pseudo: String,
  email: String,
  password: String
}, {
  strict: false,
  versionKey: false
})

const Users = mongoose.model('users', usersSchema)

module.exports = Users
