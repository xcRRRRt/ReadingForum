function show_toast(head_bg_class, strong_text, small_text, body_text) {
    const toastLive = $("#liveToast");
    toastLive.find(".toast-header").removeClass().addClass("toast-header " + head_bg_class);
    toastLive.find("strong").html(strong_text);
    toastLive.find("small").html(small_text);
    toastLive.find(".toast-body").html(body_text);
    const toast = new bootstrap.Toast(toastLive);
    toast.show();
}

$(document).ready(function () {
    const urlParams = new URLSearchParams(window.location.search);
    // 检查是否需要显示 Toast
    if (urlParams.has('show_toast') && urlParams.get('show_toast') === 'true') {
        const head_bg_class = urlParams.get('head_bg_class');
        const strong_text = urlParams.get('strong_text');
        const small_text = urlParams.get('small_text');
        const body_text = urlParams.get('body_text');
        show_toast(head_bg_class, strong_text, small_text, body_text);
    }
})