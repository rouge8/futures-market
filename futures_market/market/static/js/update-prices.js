function updatePrices(market) {
    $.getJSON('/prices/' + market + '/', function(data) {
        var stocks = [];

        $.each(data, function(index, stock) {
            stocks.push('<li id="' + stock.name + '">' + stock.name +
                "'s last price: " + stock.last_sale_price + ' at ' +
                stock.last_sale_time + ' (best buy offer: ' + stock.best_buy +
                '; best sell offer: ' + stock.best_sale + ')</li>');
        });

        $('<ul/>', {
            'id': 'stock-list',
            html: stocks.join('')
        }).replaceAll('#stock-list');
    });
};

