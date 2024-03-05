/**
 * 表单验证脚本
 * 该脚本包含了用于注册表单验证的一些函数，通过 jQuery 进行 DOM 操作。
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
 * 检查两次输入的密码是否相等，并根据检查结果更新样式和错误提示信息。
 * @returns {boolean} - 如果密码相等返回 true，否则返回 false。
 */
function check_password_equal() {
    // 获取密码和确认密码输入框的 jQuery 对象
    let password = $("#password").val();
    let password_ensure = $("#password-ensure");

    // 获取用于显示错误信息的 jQuery 对象
    let feedback = $("#password-ensure-feedback");

    // 检查密码是否相等
    if (password === password_ensure.val()) {
        // 如果密码相等，移除错误样式，添加成功样式，并清空错误提示信息
        password_ensure.removeClass("is-invalid").addClass("is-valid");
        feedback.text("");
        return true;
    } else {
        // 如果密码不相等，移除成功样式，添加错误样式，并显示错误提示信息
        password_ensure.removeClass("is-valid").addClass("is-invalid");
        feedback.text("两次密码输入不同");
        return false;
    }
}

/**
 * 检查输入框内容的长度是否在指定范围内，根据检查结果更新样式和错误提示信息。
 * @param {string} id - 输入框的 id。
 * @param {number} min - 允许的最小长度。
 * @param {number} max - 允许的最大长度。
 * @returns {boolean} - 如果输入框内容长度在指定范围内返回 true，否则返回 false。
 */
function check_length(id, min, max) {
    // 获取输入框和用于显示错误信息的 jQuery 对象
    let inputElement = $("#" + id);
    let feedback = $("#" + id + "-feedback");

    // 获取输入框内容的长度
    let inputLength = inputElement.val().length;
    // 检查输入框内容长度是否在指定范围内, 根据长度进行提示
    if (inputLength < min) {    // 太长
        inputElement.removeClass("is-valid").addClass("is-invalid");
        feedback.text("太短，最少" + min + "个字符");
        return false;
    } else if (inputLength > max) { // 太短
        inputElement.removeClass("is-valid").addClass("is-invalid");
        feedback.text("太长，最多" + max + "个字符");
        return false;
    } else {
        inputElement.removeClass("is-invalid").addClass("is-valid");
        feedback.text("");
        return true;
    }
}

/**
 * 发送用户名重复检查的 AJAX 请求，并根据结果更新样式和错误提示信息。
 * TODO 用户在哪里转到注册页面，登录后就重定向到原来的页面
 */
function ajax_username_duplicated() {
    $.ajax({
        url: "/user/register/",
        type: "post",
        data: {
            "username": $("#username").val(),
            "password": $("#password").val(),
            "password-ensure": $("#password-ensure").val(),
            "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val()
        },
        dataType: 'json',
        // 如果请求成功
        success: function (res) {
            if (res.username_error) {
                $("#username-feedback").text(res.username_error);
                let username_input = $("#username");
                username_input.val("");
                username_input.removeClass("is-valid").addClass("is-invalid");
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
    // TODO 可以优化为onblur，输入框失去焦点后立即进行判断
    // TODO 同时对多个输入框进行检验
    $("#submit").click(function () {
        if (check_not_null("username") && check_not_null("password") &&
            check_not_null("password-ensure") && check_password_equal() &&
            check_length("username", 5, 20) && check_length("password", 8, 20)) {
            // 如果所有检查通过，执行用户名重复检查的 AJAX 请求
            ajax_username_duplicated();
        }
    })
});

