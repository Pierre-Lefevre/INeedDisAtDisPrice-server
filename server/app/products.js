const express = require('express'),
  router = express.Router(),
  Products = require('../models/Products.js')

router.get('/api/products', function (req, res) {
  Products.find({}).then(eachOne => {
    res.json(eachOne)
  })
})

router.get('/api/product/:id', function (req, res) {
  Products.findOne({_id: req.params.id}).then(eachOne => {
    res.json(eachOne)
  })
})

// app.post('/api/signatures', function (req, res) {
//   console.log(req.query)
//   Signature.create({
//     guestSignature: req.query.SignatureOfGuest,
//     message: req.query.MessageofGuest,
//   }).then(signature => {
//     res.json(signature)
//   })
// })

module.exports = router
