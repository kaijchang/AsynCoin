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
            error: function(xhr, status, error) {
                $("#icon").attr("src", "images/failure.png");
            }
        })

        return false;
    });

    $("#sendtransaction").submit(function(e) {
        if ($("#privatekey").val().length != 48) {
            $(".alert").remove();
            $("#sendtransaction").prepend(`<div class="alert alert-danger">
                              <strong>Error!</strong> Your Private Key must be exactly 48 characters long.
                          </div>`);
        } else if ($("#recipient").val().length != 96) {
            $(".alert").remove();
            $("#sendtransaction").prepend(`<div class="alert alert-danger">
                            <strong>Error!</strong> Recipient's address must be exactly 96 Characters long.
                          </div>`);
        } else if (isNaN($("#amount").val())) {
            $(".alert").remove();
            $("#sendtransaction").prepend(`<div class="alert alert-danger">
                            <strong>Error!</strong> The transaction amount must be a valid number.
                          </div>`);
        } else if (isNaN($("#fee").val())) {
            $(".alert").remove();
            $("#sendtransaction").prepend(`<div class="alert alert-danger">
                            <strong>Error!</strong> The transaction fee must be a valid number.
                          </div>`);
        } else {
            var key = new sjcl.ecc.ecdsa.secretKey(
                sjcl.ecc.curves.c192,
                sjcl.ecc.curves.c192.field.fromBits(sjcl.codec.hex.toBits($("#privatekey").val()))
            );

            var pub = sjcl.ecc.basicKey.generateKeys('ecdsa')(key._curve, null, key._exponent).pub; // idk if this how you do

            if (sjcl.codec.hex.fromBits(pub.get().x.concat(pub.get().y)) == $("#recipient").val()) {
                $(".alert").remove();
                $("#sendtransaction").prepend(`<div class="alert alert-danger">
                                <strong>Error!</strong> You can't send a transaction to yourself.
                            </div>`);
            } else {
                $.ajax({
                    url: "http://" + $("#node-uri").val() + "/balance/" + sjcl.codec.hex.fromBits(pub.get().x.concat(pub.get().y)),
                    success: function(balance) {
                        $("#icon").attr("src", "images/success.png");
                        if (parseInt(balance) < parseInt($("#fee").val()) + parseInt($("#amount").val())) {
                            $(".alert").remove();
                            $("#sendtransaction").prepend(`<div class="alert alert-danger">
                                            <strong>Error!</strong> You don't have enough coins. You only have ` + balance + ` coins.
                                        </div>`);
                        } else {
                            $.get("http://" + $("#node-uri").val() + "/nonce/" + sjcl.codec.hex.fromBits(pub.get().x.concat(pub.get().y)), function(nonce) {
                                var to = $("#recipient").val();
                                var from_ = sjcl.codec.hex.fromBits(pub.get().x.concat(pub.get().y));
                                var amount = parseInt($("#amount").val());
                                var timestamp = +new Date();
                                var nonce = parseInt(nonce);
                                var fee = parseInt($("#fee").val());

                                var signature = sjcl.codec.hex.fromBits(key.sign(sjcl.hash.sha1.hash(sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(to + from_ + amount + fee + nonce + timestamp)))));

                                $.ajax({
                                    type: "POST",
                                    traditional: true,
                                    url: "http://" + $("#node-uri").val() + "/transaction",
                                    data: JSON.stringify({
                                        "to": to,
                                        "from_": from_,
                                        "amount": amount,
                                        "timestamp": timestamp,
                                        "signature": signature,
                                        "nonce": nonce,
                                        "fee": fee
                                    }),
                                    success: function(response) {

                                    }
                                });
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        $(".alert").remove();
                        $("#sendtransaction").prepend(`<div class="alert alert-danger">
                                        <strong>Error!</strong> Unable to connect to node.
                                    </div>`);
                        $("#icon").attr("src", "images/failure.png");
                    }
                });

            }
        }

        return false;
    });
});