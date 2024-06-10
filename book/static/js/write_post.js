$(document).ready(function () {
    checkUserLogin().then(function (is_login) {
        if (!is_login) {
            $("#book-detail-write-post").on('click', function (event) {
                event.preventDefault();
                let login_url = $("#navbar-login").attr("href");
                show_toast("text-bg-warning", "错误提示", "", "用户未登录&nbsp;&nbsp;&nbsp;" + "<a href='" + login_url + "'>立即登录</a>");
            });
        }
    });
});