// $(window).onload(function () {
//     $("#admin-search").val("");
// })

$(document).ready(function () {
    ajax_load_page();
    $("#admin-table .page-item").on("click", change_page);
    $("#admin-search").on('blur', search);
});

function search() {
    let to_search = $("#admin-search").val()
    let href = window.location.pathname + "?page=1";
    $.ajax({
        url: href,
        method: 'get',
        data: {
            'to_search': to_search
        },
        success: function (res) {
            load_table(res)
        }
    });
}

/**
 * 异步加载第一页表格
 */
function ajax_load_page() {
    let href = window.location.pathname + "?page=1";
    $.ajax({
        url: href,
        method: 'get',
        success: function (res) {
            console.log(res);
            load_table(res)
        }
    });
}

/**
 * 页码的点击事件
 * @param event
 */
function change_page(event) {
    event.preventDefault();
    let href = $(this).find("a").attr("href");  // 获取页码的链接
    if ($(this).hasClass("disabled")) {
        return;
    }
    $.ajax({
        url: href,
        method: "get",
        success: function (res) {
            console.log(res);
            load_table(res);
        }
    });
}

function change_sort_state(sort_btn) {
    return function (event) {
        let href = $(".page-item.active a").attr('href');
        let field = sort_btn.parent().attr("field")
        let up = sort_btn.find("span.sort-up");
        let down = sort_btn.find("span.sort-down");
        let is_asc = down.css("visibility") === "hidden";
        let is_des = up.css("visibility") === "hidden";
        let next_state;
        if (is_asc) {  // 若是升序，则下一个状态是降序
            up.css("visibility", "hidden");
            down.css("visibility", "visible");
            next_state = -1;
        } else if (is_des) {    // 若是降序，则下一个状态是默认
            up.css("visibility", "visible");
            next_state = 0;
        } else {    // 若是默认，则下一个状态是升序
            down.css("visibility", "hidden");
            next_state = 1;
        }
        $.ajax({
            url: href,
            method: "get",
            data: {
                "field": field,
                "next_state": next_state
            },
            success: function (res) {
                load_table(res);
            }
        })
    };
}

function add_table_head(required_fields, fields_name, can_sort_fields, sort_state) {
    let table = $("tbody");
    let tr = $("<tr class='table-secondary'></tr>")
    for (let i = 0; i < fields_name.length; i++) {
        let th = $("<th field='" + required_fields[i] + "'>" + fields_name[i] + "</th>");
        let to_sort_field_idx = can_sort_fields.indexOf(required_fields[i]);
        if (to_sort_field_idx > -1) {
            let up = $("<span class=\"sort-up sort-up-active\"></span>");
            let down = $("<span class=\"sort-down sort-down-active\"></span>");
            let wrapper = $("<div class='sort-btn d-inline-flex flex-column ms-1 sort'></div>")
            wrapper.on('click', change_sort_state(wrapper));
            if (sort_state[to_sort_field_idx] === 1) {
                up.css("visibility", "visible");
                down.css("visibility", "hidden");
            } else if (sort_state[to_sort_field_idx] === -1) {
                up.css("visibility", "hidden");
                down.css("visibility", "visible");
            } else {
                up.css("visibility", "visible");
                down.css("visibility", "visible");
            }
            wrapper.append(up, down);
            th.append(wrapper);
        }
        tr.append(th);
    }
    tr.append($("<th>操作</th>"))
    table.append(tr)
}


function set_search(can_search_fields, required_fields, fields_name) {
    let search = $("#admin-search")
    let search_icon = search.prev()
    if (!can_search_fields) {
        search.css("visibility", "hidden");
        search_icon.css("visibility", "hidden");
        return;
    }
    let can_search_field_names = [];
    for (let can_search_field of can_search_fields) {
        let idx = required_fields.indexOf(can_search_field);
        can_search_field_names.push(fields_name[idx]);
    }
    let place_holder = can_search_field_names.join(",");
    search.attr("placeholder", place_holder);
    search.css("visibility", "visible");
    search_icon.css("visibility", "visible")
}

/**
 * 加载表格
 * @param paginator 分页器，包含objs物品列表, neighbor_pages邻居页, page_next下一页, page_now当前页, page_prev前一页, total_pages总页数
 */
function load_table(paginator) {
    let obj_list = paginator['objs'];
    let required_fields = paginator['field'];
    let fields_name = paginator['field_name'];
    let can_sort_fields = paginator['can_sort_fields'];
    let can_search_fields = paginator['can_search_fields'];
    let can_choose_fields = paginator['can_choose_fields'];
    let sort_state = paginator['sort_state'];
    let neighbor_pages = paginator['neighbor_pages'];
    let page_next = paginator['page_next'];
    let page_now = paginator['page_now'];
    let page_prev = paginator['page_prev'];
    let total_page = paginator['total_pages'];

    set_search(can_search_fields, required_fields, fields_name);

    let table = $("tbody");
    table.find("tr").remove();

    add_table_head(required_fields, fields_name, can_sort_fields, sort_state);

    for (let obj of obj_list) {
        let tr = $("<tr></tr>")
        for (let field of required_fields) {
            let value = obj[field] !== undefined && obj[field] !== null ? obj[field] : '';
            tr.append($("<td></td>").text(value));
        }
        let href = window.location.pathname + "edit/" + obj.id
        tr.append('<td><a href="' + href + '">修改</a>/<a href="#">删除</a></td>')
        table.append(tr);
    }

    // 页码
    let list = $("#admin-table ul.pagination");
    list.empty()
    let first_page = $('<li class="page-item"><a class="page-link" href="' + window.location.pathname + '?page=1">第一页</a></li>')
    let prev_page = $('<li class="page-item"><a class="page-link">&lt;</a></li>')
    if (page_prev) {
        prev_page.find("a").attr("href", window.location.pathname + "?page=" + page_prev);
    } else {
        prev_page.addClass("disabled");
    }

    list.append(first_page, prev_page);

    for (let i = 0; i < neighbor_pages.length; i++) {
        let href = window.location.pathname + "?page=" + (neighbor_pages[i]);
        let page_item = $('<li class="page-item"><a class="page-link"></a></li>')
        page_item.find("a").attr("href", href);
        page_item.find("a").text(neighbor_pages[i]);
        if (neighbor_pages[i] === page_now)
            page_item.addClass("active");
        list.append(page_item);
    }

    let next_page = $('<li class="page-item"><a class="page-link">&gt;</a></li>')
    if (page_next) {
        next_page.find("a").attr("href", window.location.pathname + "?page=" + page_next);
    } else {
        next_page.addClass("disabled")
    }
    let last_page = $('<li class="page-item"><a class="page-link" href="' + window.location.pathname + '?page=' + total_page + '">最后一页</a></li>')

    list.append(next_page, last_page);

    $("#admin-table .page-item").on("click", change_page)

}