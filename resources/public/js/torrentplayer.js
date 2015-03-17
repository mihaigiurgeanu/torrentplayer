funciton torrentplayer(opts) {
    var o = $.extend({
        media_url: "/stream"
    });
    
    return {
        createStream: function(magnet_urn) {
            var request = post(o.media_url, magnet_urn);
            request.done(mediaInfo, stausText, xhr) {
                console.log("Response for createStream with status" + statusText);
            }
            request.fail(xhr, statusText, error) {
                console.log("Error creating stream: " + statusText + "/" + error);
            }
        }
    }
}
