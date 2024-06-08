// function show_toast(head_bg_class, strong_text, small_text, body_text) {
//     const toastLive = $("#liveToast");
//     toastLive.find(".toast-header").removeClass().addClass("toast-header " + head_bg_class);
//     toastLive.find("strong").html(strong_text);
//     toastLive.find("small").html(small_text);
//     toastLive.find(".toast-body").html(body_text);
//     const toast = new bootstrap.Toast(toastLive);
//     toast.show();
// }

function show_toast(head_bg_class, strong_text, small_text, body_text) {
    let _toast = $('<div class="toast" role="alert" aria-live="assertive" aria-atomic="true">')
        .append($('<div class="toast-header">')
            .append($('<strong class="me-auto">').text(strong_text))
            .append($('<small>').text(small_text))
            .append($('<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close">')))
        .append($('<div class="toast-body">').html(body_text));
    _toast.find(".toast-header").removeClass().addClass("toast-header " + head_bg_class);
    $("#toast-container").append(_toast);
    const toast = new bootstrap.Toast(_toast);
    toast.show();
}

$(document).ready(function () {
    const urlParams = new URLSearchParams(window.location.search);
    // 检查是否需要显示 Toast
    if (urlParams.has('toast') && urlParams.get('toast') === 'true') {
        const head_bg_class = urlParams.get('hbg');
        const strong_text = urlParams.get('St');
        const small_text = urlParams.get('st');
        const body_text = urlParams.get('bt');
        show_toast(head_bg_class, strong_text, small_text, body_text);
    }
})

function generate_toast_url(init_url, head_bg_class, strong_text, small_text, body_text) {
    return init_url + "?toast=true" + "&hbg=" + head_bg_class + "&St=" + strong_text + "&st=" + small_text + "&bt=" + body_text;
}