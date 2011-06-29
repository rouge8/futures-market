function updateGraph(market) {
    var options = {
        lines: { show: true },
        points: {show: true },
        xaxis: { mode: "time" } 
    };
    var data = [];
    var placeholder = $("#placeholder");

    function onDataReceived(stocks) {
        // plot each stock
        // we get all the data in one go, if we only got partial data
        // we could merge it with what we already have
        data = [];

        $.each(stocks, function(index, stock) {
            // add to current data

            data.push(stock);

            // plot!
            $.plot(placeholder, data, options);
        });
    }

    $.ajax({
        url: '/orders/' + market + '/',
        method: 'GET',
        dataType: 'json',
        success: onDataReceived
    });
};
