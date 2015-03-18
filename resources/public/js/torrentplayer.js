function torrentplayer(opts) {
    var o = $.extend( {
        mediaUrl: "/resources/streams"
    }
    ,
    opts);
    function showPalyer(mediaInfo) {
        console.log("Starting player with mediaInfo: " + JSON.stringify(mediaInfo));
        if(! o.element) {
            throw "There is no element defined for the player.";
        }
        //o.element.replaceWith("<video src='" + mediaInfo.url + "'></video>");
        // var player = new MediaElementPlayer(o.element,
        // {
        //     enablePluginDebug: true, 
        //     success: function(mediaElement) {
        //         mediaElement.pause();
        //         mediaElement.setSrc(mediaInfo.url);
        //         mediaElement.play();
        //     }
        // }
        // );
        
        o.element.attr("src", mediaInfo.url);
        $('video,audio').mediaelementplayer({
            enablePluginDebug: true
        });
    }
    return {
        createStream: function(magnetUrn) {
            var request = $.post(o.mediaUrl, magnetUrn);
            request.done(function(mediaInfo, statusText, xhr) {
                console.log("Response for createStream with status " + statusText);
                if(xhr.status= 201) {
                    console.log("Stream download created. New resource location: " + xhr.getResponseHeader('Location'));
                }
                showPalyer(mediaInfo);
            }
            );
            request.fail(function (xhr,
            statusText,
            error) {
                if(xhr.status= 409) {
                    console.log("Stream download already exists." + xhr.getResponseHeader('Location'));
                    showPalyer($.parseJSON(xhr.responseText));
                }
                console.log("Error creating stream: " + statusText + "/" + error);
            }
            );
        }
    }
}
