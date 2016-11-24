function init_search() {
    $(document).ready(function () {
        $(".found-video").each(function () {
            var $e = $(this);
            var id = $e.data("videoid");
            var word = words[id];
            var player = players[id];

            var ems = $e.find(".video-highlights em")

            for (i = 0; i < ems.length; i++) {
                $(ems[i]).click(function () {
                    player.seekTo($(this).data("time"))
                }).attr("title", word[i].word + ": " + word[i].time).data("time", word[i].time)
            }
        })

    })
}