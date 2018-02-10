const express = require('express'),
  path = require('path'),
  router = express.Router()

router.get('/api/image/:store/:name', function (req, res) {
  res.sendFile(path.join(__dirname, '..', '..', 'scrapies', 'data', req.params.store, 'img', req.params.name))
})

module.exports = router
