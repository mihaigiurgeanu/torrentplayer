function torrentplayer(opts) {
    var o = $.extend({
        mediaUrl: "/resources/streams",
        onmediainfo: function(mediainfo) {
            console.log("onmediainfo option not specified");
        }
    }, opts);
    return {
        createStream: function(magnetUrn) {
            var request = $.post(o.mediaUrl, magnetUrn);
            request.done(function(mediainfo, statusText, xhr) {
                console.log("Response for createStream with status " + statusText);
                if(xhr.status == 201) {
                    console.log("Stream download created. New resource location: " + xhr.getResponseHeader('Location'));
                }
                console.log("Playing media " + mediainfo.url);
                o.onmediainfo(mediainfo);
            });
            request.fail(function (xhr, statusText, error) {
                if(xhr.status == 409) {
                    console.log("Stream download already exists." + xhr.getResponseHeader('Location'));
                    var mediainfo = JSON.parse(xhr.responseText);
                    console.log("Playing media: " + mediainfo.url);
                    o.onmediainfo(mediainfo);
                } else {
                    console.log("Error creating stream: " + statusText + "/" + error);
                }
            });
        }
    }
}
