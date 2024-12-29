document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".starting-lineup__tab-link");
    const contents = document.querySelectorAll(".starting-lineup__tab-content");

    tabs.forEach((tab) => {
        tab.addEventListener("click", function () {
            tabs.forEach((t) => t.classList.remove("starting-lineup__tab-link--active"));
            contents.forEach((content) => content.classList.remove("starting-lineup__tab-content--active"));

            const target = this.getAttribute("data-tab");
            document.getElementById(target).classList.add("starting-lineup__tab-content--active");
            this.classList.add("starting-lineup__tab-link--active");
        });
    });
});