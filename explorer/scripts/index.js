var interval;
var ws;

function connect(URL) {
    // pings node
    $.ajax({
        url: "http://" + URL + "/height",
        success: function(height) {
            clearInterval(interval);

            var height = parseInt(height);
            var maxBlocksShown = 15;

            $("#blocks").empty();
            $("#icon").attr("src", "images/success.png");

            if (height > maxBlocksShown) {
                $.get("http://" + URL + "/blockrange/" + (height - maxBlocksShown) + "/" + (height - 1), function(blocks) {
                    for (var i = 1; i < maxBlocksShown + 1; i++) {
                        var block = blocks[blocks.length - i];
                        $("#blocks").append(`<tr>
                                                <th scope="row">` + block.index + `</th>
                                                <td>` + block.hash + `</td>
                                                <td><time class="timeago" datetime="` + new Date(block.timestamp * 1000).toISOString() + `">` + block.timestamp + `</time></td>
                                                <td>` + block.data.length + `</td>
                                             </tr>`);
                    }
                    $("time.timeago").timeago();
                });
                $("time.timeago").timeago();
            } else {
                $.get("http://" + URL + "/blockrange/0/" + (height - 1), function(blocks) {
                    for (var i = 1; i < blocks.length + 1; i++) {
                        var block = blocks[blocks.length - i];
                        $("#blocks").append(`<tr>
                                                <th scope="row">` + block.index + `</th>
                                                <td>` + block.hash + `</td>
                                                <td><time class="timeago" datetime="` + new Date(block.timestamp * 1000).toISOString() + `">` + block.timestamp + `</time></td>
                                                <td>` + block.data.length + `</td>
                                             </tr>`);
                    }
                    $("time.timeago").timeago();
                });
            }

            // subscribes to new blocks
            ws = new WebSocket("ws://" + URL + "/subscribeblock");
            ws.onmessage = function(event) {
                var block = JSON.parse(event.data);
                $("#blocks").prepend(`<tr>
                                        <th scope="row">` + block.index + `</th>
                                        <td>` + block.hash + `</td>
                                        <td><time class="timeago" datetime="` + new Date(block.timestamp * 1000).toISOString() + `">` + block.timestamp + `</time></td>
                                        <td>` + block.data.length + `</td>
                                      </tr>`);
                $("time.timeago").timeago();

                if ($("#blocks").children().length > maxBlocksShown) {
                    $("#blocks").children().last().remove();
                }
            }

            ws.onclose = function(event) {
                ws = undefined;
                $("#blocks").empty();
                $("#blocks").append(`<tr>
                                        <td colspan="4" class="text-center">Unable to Connect.</td>
                                     </tr>`);
                $("#icon").attr("src", "images/failure.png");
            }

        },
        error: function(xhr, status, error) {
            clearInterval(interval);

            $("#icon").attr("src", "images/failure.png");

            interval = setInterval(function() {
                connect($("#node-uri").val())
            }, 10000);

            if (ws != undefined) {
                ws.close();
            }
        }
    });
}

$(document).ready(function() {
    // https://stackoverflow.com/questions/20194722/can-you-get-a-users-local-lan-ip-address-via-javascript
    window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection; //compatibility for Firefox and chrome
    var pc = new RTCPeerConnection({
        iceServers: []
    });
    pc.createDataChannel(""); //create a bogus data channel
    pc.createOffer(pc.setLocalDescription.bind(pc), function() {}); // create offer and set local description
    pc.onicecandidate = function(ice) {
        if (ice && ice.candidate && ice.candidate.candidate) {
            var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];
            pc.onicecandidate = function() {};
            connect(myIP + ":8000");
            $("#node-uri").attr("value", myIP + ":8000");
            $("#node-uri").on("input", function() {
                connect(this.value);
            });
        }
    }
});