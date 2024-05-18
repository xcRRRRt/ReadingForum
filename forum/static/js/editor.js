$(document).ready(function () {
    $(".django-ckeditor-widget").css({'width': '100%'});

    // 文章标签
    let labels_all = $("#labels-chosen");
    labels_all.on("click", "button", function () {
        $(this).parent().remove();
    });
    $("#label-add").click(function () {
        let input = $(this).prev();
        let input_val = input.val();
        if (input_val.trim().length !== 0) {
            if ($("#labels-chosen div").length >= 6) {
                show_toast("text-bg-warning", "提示", "", "标签太多啦！")
                return;
            }
            const label = $("<div class=\"border rounded-pill px-2 bg-secondary-subtle me-2 mb-2\"></div>");
            const remove = $("<button type='button'>×</button>");
            const span = $("<span></span>")
            span.text(input_val);
            label.append(span, remove);
            labels_all.append(label);
            input.val("");
        }
    });

    // 发布文章
    $("#ckeditor-submit").click(function (event) {
        event.preventDefault();
        // 标题
        let title_input = $("#editor-post-title");
        let title = title_input.val().trim();
        if (title.length < 5 || title.length > 30) {
            title_input.attr("class", "form-control is-invalid");
            title_input.next().text("应在5-50个字符之间(当前字符数" + title.length + ")")
            return;
        }
        title_input.attr("class", "form-control");
        $("#id_title").val(title);
        // 标签
        let labels = ""
        $("#labels-chosen span").each(function () {
            labels += $(this).text() + " "
        })
        labels = labels.trim();
        $("#id_labels").val(labels);
        $("#ckeditor-form").submit();
    })

    // 提交表单反馈
    let feedback = $("#editor-invalid-feedback").text();
    if (feedback.trim().length !== 0) {
        let hint = "";
        if (feedback.trim() === "这个字段是必填项。") {
            hint = "文章空空如也"
        }
        show_toast("text-bg-danger", "发布失败", "", hint);
    }
})

// function show_toast(head_bg_class, strong_text, small_text, body_text) {
//     const toastLive = $("#liveToast");
//     toastLive.find(".toast-header").removeClass().addClass("toast-header " + head_bg_class);
//     toastLive.find("strong").text(strong_text);
//     toastLive.find("small").text(small_text);
//     toastLive.find(".toast-body").text(body_text);
//     const toast = new bootstrap.Toast(toastLive);
//     toast.show();
// }
