document.addEventListener("DOMContentLoaded", function () {
    const mainTabLinks = document.querySelectorAll(".main-tab-controls .main-tab-link");
    const mainTabContents = document.querySelectorAll(".main-tabs .main-tab-content");

    mainTabLinks.forEach((link) => {
        link.addEventListener("click", function () {
            mainTabLinks.forEach((tab) => tab.classList.remove("active"));
            mainTabContents.forEach((content) => content.classList.remove("active"));

            const target = this.getAttribute("data-tab");
            document.getElementById(target).classList.add("active");
            this.classList.add("active");
        });
    });
});
