const express = require('express'),
  router = express.Router(),
  Alerts = require('../models/Alerts.js')

router.post('/alert', function (req, res) {
  let alert = req.body
  Alerts.create(alert).then(createdAlert => {
    res.json(createdAlert)
  })
})

module.exports = router
