$(document).ready(function () {
    let create_post_btn = $("#create-post-btn");
    create_post_btn.on("click", function (event) {
        checkUserLogin().then(function (is_login) {
            if (!is_login) {
                let login_url = $("#navbar-login").attr("href");
                show_toast("text-bg-warning", "错误提示", "", "用户未登录&nbsp;&nbsp;&nbsp;" + "<a href='" + login_url + "'>立即登录</a>");
            } else {
                window.location.href = create_post_btn.attr("href");
            }
        });
    })
})