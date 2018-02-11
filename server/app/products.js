const express = require('express'),
  router = express.Router(),
  fs = require('fs'),
  path = require('path'),
  utils = require('../utils/utils'),
  Products = require('../models/Products.js')

router.get('/api/products', async function (req, res) {
  let query = {}
  let page = req.query.page && typeof parseInt(req.query.page) === 'number' ? req.query.page : 1
  let pageSize = 40

  if (req.query.search) {
    query.name = {$regex: '.*' + req.query.search.toLowerCase() + '.*', $options: 'i'}
  }

  let products = await Products.find(query).skip(pageSize * (page - 1)).limit(pageSize)
  let nbPage = Math.ceil(await Products.find(query).count() / pageSize)

  await utils.asyncForEach(products, async (product, i) => {
    if (!fs.existsSync(path.join(__dirname, '..', '..', 'scrapies', 'data', product.store, 'img', product.image_name + '.jpg'))) {
      products[i].image_name = 'default'
    }

    let minPrice = product.price
    let maxPrice = product.price

    let similarProducts = await Products.find({'_id': {$in: product.similarities}})

    await utils.asyncForEach(similarProducts, async (similarProduct) => {
      if (similarProduct.price < minPrice) {
        minPrice = similarProduct.price
      } else if (similarProduct.price > minPrice) {
        maxPrice = similarProduct.price
      }
    })

    product.minPrice = minPrice
    product.maxPrice = maxPrice
  })

  res.json({products, nbPage})
})

router.get('/api/product/:id', async function (req, res) {
  let product = await Products.findOne({'_id': req.params.id})
  if (!fs.existsSync(path.join(__dirname, '..', '..', 'scrapies', 'data', product.store, 'img', product.image_name + '.jpg'))) {
    product.image_name = 'default'
  }
  let similarProducts = await Products.find({'_id': {$in: product.similarities}})
  res.json({product, similarProducts})
})

module.exports = router
