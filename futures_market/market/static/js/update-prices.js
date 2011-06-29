function updatePrices(market) {
    // gets latest prices as JSON data
    $.getJSON('/prices/' + market + '/', function(data) {
        var stocks = [];

        // iterates over stocks and assembles them into nicely formatted lists
        $.each(data, function(index, stock) {
            stocks.push('<li id="' + stock.name + '">' + stock.name +
                "'s last price: " + stock.last_sale_price + ' at ' +
                stock.last_sale_time + ' (best buy offer: ' + stock.best_buy +
                '; best sell offer: ' + stock.best_sale + ')</li>');
        });

        // joins all the stock list into an unordered list and replaces the
        // previous one
        $('<ul/>', {
            'id': 'stock-list',
            html: stocks.join('')
        }).replaceAll('#stock-list');
    });
};

