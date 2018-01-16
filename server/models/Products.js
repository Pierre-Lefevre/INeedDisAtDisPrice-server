const mongoose = require('mongoose')

let Schema = mongoose.Schema

const productsSchema = new Schema({
  name: {
    type: mongoose.Schema.Types.Mixed,
    required: true,
  },
})

const Products = mongoose.model('products', productsSchema)

module.exports = Products
