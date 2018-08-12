var interval;

function connect(URL) {
    $.ajax({
        url: "http://" + URL + "/config",
        success: function(config) {
            clearInterval(interval);

            $.get("http://" + URL + "/height", function(height) {
                var height = parseInt(height);

                $("#icon").attr("src", "images/success.png");

                $("#difficulty").append('<li class="list-group-item">' + config["INITIAL_DIFFICULTY"] * 16 + ' H per Block</li>');
                $("#difficulty").append('<li class="list-group-item">' + config["DIFFICULTY_ADJUST"] + ' Blocks Between Difficulty Adjustments</li>');

                $("#blockreward").append('<li class="list-group-item">' + config["INITIAL_REWARD"] / 2**Math.floor(height / config["REWARD_HALVING"]) + " Coins per Block</li>")
                $("#blockreward").append('<li class="list-group-item">Reward Halving Every ' + config["REWARD_HALVING"] + " Blocks</li>")
            });
        },
        error: function(xhr, status, error) {
            clearInterval(interval);

            $('#icon').attr("src", "images/failure.png");

            interval = setInterval(function(){connect($('#node-uri').val())}, 10000);
        }
    });
}


$(document).ready(function() {
    // https://stackoverflow.com/questions/20194722/can-you-get-a-users-local-lan-ip-address-via-javascript
    window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection; //compatibility for Firefox and chrome
    var pc = new RTCPeerConnection({iceServers:[]});    
    pc.createDataChannel(''); //create a bogus data channel
    pc.createOffer(pc.setLocalDescription.bind(pc), function(){});// create offer and set local description
    pc.onicecandidate = function(ice) {
        if (ice && ice.candidate && ice.candidate.candidate) {
            var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];  
            pc.onicecandidate = function(){};
            connect(myIP + ":8000");
            $("#node-uri").attr("value", myIP + ":8000");
            $("#node-uri").on("input", function() {
                connect(this.value);
            });
        }
    }
});
