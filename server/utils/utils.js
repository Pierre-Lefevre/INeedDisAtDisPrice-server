module.exports = {

  currencySymbol (value) {
    let symbols = {
      'EUR': '€',
      'USD': '$',
      'GBP': '£'
    }
    return symbols[value]
  },

  async asyncForEach (array, callback) {
    for (let index = 0; index < array.length; index++) {
      await callback(array[index], index, array)
    }
  }
}
