const express = require('express'),
  router = express.Router(),
  utils = require('../utils/utils'),
  Alerts = require('../models/Alerts.js'),
  Products = require('../models/Products.js')

router.post('/alert', function (req, res) {
  let alert = req.body
  alert.price = parseInt(alert.price)
  Alerts.create(alert).then(createdAlert => {
    res.json(createdAlert)
  })
})

router.get('/api/alerts/:id_user', async function (req, res) {
  let idUser = req.params.id_user
  let alerts = await Alerts.find({id_user: idUser})
  await utils.asyncForEach(alerts, async (alert, i) => {
    alerts[i].product = await Products.findOne({'_id': alert.id_product})
  })
  res.json(alerts)
})

module.exports = router
