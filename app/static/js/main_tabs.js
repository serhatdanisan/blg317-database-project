document.addEventListener("DOMContentLoaded", function () {
    const mainTabLinks = document.querySelectorAll(".main-tab-controls .main-tab-link");
    const mainTabContents = document.querySelector(".main-tab-contents");
    const sideContainer = document.querySelector(".side-container");

    mainTabLinks.forEach((link) => {
        link.addEventListener("click", function () {
            mainTabLinks.forEach((tab) => tab.classList.remove("active"));
            const target = this.getAttribute("data-tab");

            document.querySelectorAll(".main-tab-content").forEach((content) => {
                content.classList.remove("active");
            });

            document.getElementById(target).classList.add("active");
            this.classList.add("active");

            if (target === "main-tab-event-maps") {
                sideContainer.style.display = "none";
                mainTabContents.style.flex = "1";
            } else {
                sideContainer.style.display = "flex";
                mainTabContents.style.flex = "0.75";
            }
        });
    });
});