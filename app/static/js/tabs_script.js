document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".tab-link");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach((tab) => {
        tab.addEventListener("click", function () {
            tabs.forEach((t) => t.classList.remove("active"));
            contents.forEach((content) => content.classList.remove("active"));

            const target = this.getAttribute("data-tab");
            document.getElementById(target).classList.add("active");
            this.classList.add("active");
        });
    });
});
