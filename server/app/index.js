const express = require('express'),
  app = express(),
  bodyParser = require('body-parser'),
  path = require('path'),
  expressValidator = require('express-validator'),
  mongoose = require('mongoose'),
  cors = require('cors'),
  products = require('./products'),
  url = 'mongodb://localhost:27017/iNeedDisAtDisPrice',
  port = 4242

app.use(bodyParser.urlencoded({extended: false}))
app.use(bodyParser.json())
app.use(cors())
app.use(products)

mongoose.connect(url, function (err, db) {
  if (err) {
    console.log('Unable to connect to the MongoDB server (' + err + ')')
  } else {
    console.log('Connection established with the MongoDB server (' + url + ')')
  }
})

app.listen(port, function () {
  console.log('i-need-dis-at-dis-price-server listening on port : ' + port + '.')
})
