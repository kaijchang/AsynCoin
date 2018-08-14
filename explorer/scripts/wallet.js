$(document).ready(function() {
    // https://stackoverflow.com/questions/20194722/can-you-get-a-users-local-lan-ip-address-via-javascript
    window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection; //compatibility for Firefox and chrome
    var pc = new RTCPeerConnection({
        iceServers: []
    });
    pc.createDataChannel(''); //create a bogus data channel
    pc.createOffer(pc.setLocalDescription.bind(pc), function() {}); // create offer and set local description
    pc.onicecandidate = function(ice) {
        if (ice && ice.candidate && ice.candidate.candidate) {
            var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];
            pc.onicecandidate = function() {};
            $("#node-uri").attr("value", myIP + ":8000");
        }
    }

    $("#generatekeys").submit(function(e) {
        var keys = sjcl.ecc.ecdsa.generateKeys(192);

        $("#private").text("Private Key: " + sjcl.codec.hex.fromBits(keys.sec.get()));
        $("#address").text("Address: " + sjcl.codec.hex.fromBits(keys.pub.get().x.concat(keys.pub.get().y)));

        return false;
    });

    $("#checkbalance").submit(function(e) {
        $.ajax({
            url: "http://" + $("#node-uri").val() + "/balance/" + $("#balance_address").val(),
            success: function(balance) {
                $("#icon").attr("src", "images/success.png");
                $("#balance").text("Balance: " + balance);
            },
            failure: function(xhr, status, error) {
                $("#icon").attr("src", "images/failure.png");
            }
        })

        return false;
    });
});
