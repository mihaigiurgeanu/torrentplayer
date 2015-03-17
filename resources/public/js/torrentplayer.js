function torrentplayer(opts) {
    var o = $.extend({
        media_url: "/resources/streams"
    });
    
    return {
        createStream: function(magnet_urn) {
            var request = $.post(o.media_url, magnet_urn);
            request.done(function(mediaInfo, statusText, xhr) {
                console.log("Response for createStream with status" + statusText);
                if(xhr.status == 201) {
                    console.log("Resource created. New resource location: " + xhr.getResponseHeader('Location'));
                }
            });
            request.fail(function (xhr, statusText, error) {
                console.log("Error creating stream: " + statusText + "/" + error);
            });
        }
    }
}
