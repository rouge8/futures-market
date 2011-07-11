function updateGraph(url) {
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

            if (stock.data.length > 0) {
                var last_price = stock.data[stock.data.length-1][1];
                d = new Date();
                utc = d.getTime();
                //localOffset = d.getTimezoneOffset() * 60000;
                //utc = localTime + localOffset;
                offset = -5;
                var now = utc + (3600000*offset);

                var current = new Array(now, last_price);
                stock.data.push(current);
                //console.log(now);
                //console.log(last_price);
                console.log(stock);
            }
            data.push(stock);

            // plot!
            $.plot(placeholder, data, options);
        });
    }

    $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        success: onDataReceived
    });
};
