/**
 * 不知道为什么无法从另一个js文件里导入，加上export就不行，就很amazing
 * import {check_not_null} from "./check_register";
 */

/**
 * 检查输入框内容是否不为空，根据检查结果更新样式和错误提示信息。
 * @param {string} id - 输入框的 id。
 * @returns {boolean} - 如果输入框内容不为空返回 true，否则返回 false。
 */
function check_not_null(id) {
    // 获取输入框和用于显示错误信息的 jQuery 对象
    let inputElement = $("#" + id);
    let feedback = $("#" + id + "-feedback");

    // 检查输入框内容是否为空
    if (inputElement.val().length === 0) {
        // 如果为空，移除成功样式，添加错误样式，并显示错误提示信息
        inputElement.removeClass("is-valid").addClass("is-invalid");
        feedback.text("不能为空");
        return false;
    } else {
        // 如果不为空，移除错误样式，添加成功样式，并清空错误提示信息
        inputElement.removeClass("is-invalid").addClass("is-valid");
        feedback.text("");
        return true;
    }
}

/**
 * 发送用户登录的 AJAX 请求，并根据结果更新样式和错误提示信息。
 * TODO 用户在哪里转到登录页面，登录后就重定向到原来的页面
 */
function ajax_valid_login() {
    $.ajax({
        url: "/user/login/",
        type: "post",
        data: {
            "username": $("#username").val(),
            "password": $("#password").val(),
            "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val()
        },
        dataType: 'json',
        // 如果请求成功
        success: function (res) {
            // 找不到该用户名
            if (res.username_error) {
                $("#username-feedback").text(res.username_error);
                let username_input = $("#username");
                username_input.val("");
                username_input.removeClass("is-valid").addClass("is-invalid");
            }
            // 密码错误
            if (res.password_error) {
                $("#password-feedback").text(res.password_error);
                let password_input = $("#password");
                password_input.val("");
                password_input.removeClass("is-valid").addClass("is-invalid");
            }
            if (res.is_success) {
                window.location.href = "/forum/";
            }
        },
        // 如果请求失败
        error: function (res) {

        }
    });
}

// 在document加载完毕后开始绑定
$(document).ready(function () {
    $("#submit").click(function () {
        if (check_not_null("username") && check_not_null("password")) {
            // 如果所有检查通过，尝试登录
            ajax_valid_login();
        }
    });
});
