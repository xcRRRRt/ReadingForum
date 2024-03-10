// 获取所有具有 "breadcrumb" class 的元素
var breadcrumbs = document.getElementsByClassName("breadcrumb");

// 确保至少有一个 breadcrumb 元素存在
if (breadcrumbs.length > 0) {
    // 获取最后一个 breadcrumb 元素
    var lastBreadcrumb = breadcrumbs[breadcrumbs.length - 1];

    // 添加 "active" class 到最后一个 breadcrumb 元素
    lastBreadcrumb.classList.add("active");
}