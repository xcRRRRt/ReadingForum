$(document).ready(function () {
    let search_type_span = $("#search-type");
    let search_input = $("#search-input");
    let search_btn = $("#search-btn");
    let search_options = $("#search-options li");
    let href = '';
    let type = "1";

    search_options.on("click", function () {
        type = $(this).attr("data-search-type");
        search_type_span.text($(this).text());
        if (type === "1") {
            search_input.attr("placeholder", "搜索")
        } else if (type === "2") {
            search_input.attr("placeholder", "以空格分割多个标签")
        }
    });

    search_btn.on("click", function (event) {
        search(event);
    });

    // 监听输入框的键盘事件
    search_input.on("keypress", function (event) {
        // 如果按下的键是回车键
        if (event.keyCode === 13) {
            search(event);
        }
    });

    // 执行搜索操作的函数
    function search(event) {
        event.preventDefault();
        let search_val = search_input.val().trim();
        if (search_val === '') {
            show_toast("bg-warning", "提示", "", "内容不能为空");
        } else {
            if (type === "1") {
                search_val = search_val.replace(/\s+/g, '')
                href = "/search/?q=" + search_val;
                window.location.href = href;
            } else if (type === "2") {
                let to_search_labels = search_val.split(" ")
                to_search_labels = to_search_labels.join("+");
                href = "/search-labels/?label=" + to_search_labels;
                window.location.href = href;
            }
        }
    }
});