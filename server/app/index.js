const express = require('express'),
  app = express(),
  bodyParser = require('body-parser'),
  path = require('path'),
  expressValidator = require('express-validator'),
  mongoose = require('mongoose'),
  cors = require('cors'),
  config = require('../config/config'),
  products = require('./products'),
  images = require('./images'),
  users = require('./users'),
  alerts = require('./alerts')

app.use(bodyParser.urlencoded({extended: true}))
app.use(bodyParser.json())
app.use(cors())
app.use(products)
app.use(images)
app.use(users)
app.use(alerts)

mongoose.connect(config.mongoUrl, function (err, db) {
  if (err) {
    console.log('Unable to connect to the MongoDB server (' + err + ')')
  } else {
    console.log('Connection established with the MongoDB server (' + config.mongoUrl + ')')
  }
})

app.listen(config.portListen, function () {
  console.log('i-need-dis-at-dis-price-server listening on port : ' + config.portListen + '.')
})
