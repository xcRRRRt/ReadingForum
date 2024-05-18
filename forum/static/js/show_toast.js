function show_toast(head_bg_class, strong_text, small_text, body_text) {
    const toastLive = $("#liveToast");
    toastLive.find(".toast-header").removeClass().addClass("toast-header " + head_bg_class);
    toastLive.find("strong").html(strong_text);
    toastLive.find("small").html(small_text);
    toastLive.find(".toast-body").html(body_text);
    const toast = new bootstrap.Toast(toastLive);
    toast.show();
}