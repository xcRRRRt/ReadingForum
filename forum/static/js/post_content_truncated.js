$(document).ready(function () {
    set_post_content_truncated();
});

function set_post_content_truncated() {
    $(".post-content-truncated").each(function () {
        let $imgs = $(this).find("img");
        $imgs.hide();
        let $first_img = $imgs.eq(0);
        $first_img.css({"margin-bottom": "10px", 'height': '', 'width': ''});
        $first_img.show();
        $(this).append($first_img);
    });
}