const express = require('express'),
  router = express.Router(),
  Users = require('../models/Users.js')

router.post('/sign-in', function (req, res) {
  let pseudo = req.body.pseudo
  let password = req.body.password
  Users.findOne({pseudo, password}).then(user => {
    if (user) {
      res.json({login: true, user})
    } else {
      res.json({login: false})
    }
  })
})

router.post('/sign-up', function(req, res) {
  let user = req.body
  Users.create(user).then(createdUser => {
    res.json(createdUser)
  })
});

module.exports = router
