var interval;
var ws;

function connect(URL) {
    // pings node
    $.ajax({
        url: "http://" + URL + "/blocks",
        success: function(blocks) {
            clearInterval(interval);
            $('#blocks').empty();
            if (blocks.length > 10) {
                for (var i = 1; i < 11; i++) {
                    var block = blocks[blocks.length - i];
                    $('#blocks').append(`<tr>
                                            <th scope="row">` + block.index + `</th>
                                            <td>` + block.hash + `</td>
                                            <td><time class="timeago" datetime="` + new Date(block.timestamp * 1000).toISOString() +`">` + block.timestamp + `</time></td>
                                            <td>` + block.data.length + `</td>
                                         </tr>`);
                }
            }
            else {
                for (var i = 1; i < blocks.length + 1; i++) {
                    var block = blocks[blocks.length - i];
                    $('#blocks').append(`<tr>
                                            <th scope="row">` + block.index + `</th>
                                            <td>` + block.hash + `</td>
                                            <td><time class="timeago" datetime="` + new Date(block.timestamp * 1000).toISOString() +`">` + block.timestamp + `</time></td>
                                            <td>` + block.data.length + `</td>
                                         </tr>`);
                }
            }

            $("time.timeago").timeago();

            // subscribes to new blocks
            $('#icon').attr("src", "images/success.png");

            if (ws == undefined) {
                ws = new WebSocket("ws://" + URL + "/subscribeblock");
                ws.onmessage = function(event) {
                    var block = JSON.parse(event.data);
                    $('#blocks').prepend(`<tr>
                                            <th scope="row">` + block.index + `</th>
                                            <td>` + block.hash + `</td>
                                            <td><time class="timeago" datetime="` + new Date(block.timestamp * 1000).toISOString() +`">` + block.timestamp + `</time></td>
                                            <td>` + block.data.length + `</td>
                                          </tr>`);
                    $("time.timeago").timeago();
    
                    if ($("#blocks").children().length > 10) {
                        $("#blocks").children().last().remove();
                    }
                }
    
                ws.onclose = function(event) {
                    ws = undefined;

                    $('#blocks').empty();
                    $('#blocks').append(`<tr>
                                            <td colspan="4" id="noresults" class="text-center">Unable to Connect.</td>
                                         </tr>`);
                    $('#icon').attr("src", "images/failure.png");

                    interval = setInterval(function(){connect($('#node-uri').val())}, 10000);
                }
            }
        },
        error: function(xhr, status, error) {
            clearInterval(interval);

            $('#icon').attr("src", "images/failure.png");

            interval = setInterval(function(){connect($('#node-uri').val())}, 10000);

            if (ws != undefined) {
                ws.close();
            }
        }
    });
}

$(document).ready(function() {
    connect('127.0.0.1:8000');
    $('#node-uri').on('input', function() {
        connect(this.value);
    });
});
