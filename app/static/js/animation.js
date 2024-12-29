function animateNumber(element, targetValue, duration) {
  let startValue = 0;
  const increment = 1;
  const stepTime = duration / targetValue;

  const interval = setInterval(function () {
    startValue += increment;
    if (startValue >= targetValue) {
      clearInterval(interval);
      element.textContent = targetValue;
    } else {
      element.textContent = startValue;
    }
    element.style.opacity = 1;
  }, stepTime);
}

document.querySelectorAll(".stat-value").forEach(function (element) {
  const targetValue = parseInt(element.getAttribute("data-target"));
  const duration = 1000;
  animateNumber(element, targetValue, duration);
});

document.addEventListener("DOMContentLoaded", function () {
  const tableHead = document.querySelector(".matches-table-thead");
  const tableRows = document.querySelectorAll(".matches-table-row");

  if (tableHead) {
    tableHead.style.opacity = 0;
    tableHead.style.transform = "translateY(20px)";
  }
  tableRows.forEach((row) => {
    row.style.opacity = 0;
    row.style.transform = "translateY(20px)";
  });

  setTimeout(() => {
    if (tableHead) {
      tableHead.style.opacity = 1;
      tableHead.style.transform = "translateY(0)";
    }
  }, 100);

  tableRows.forEach((row, index) => {
    setTimeout(() => {
      row.style.opacity = 1;
      row.style.transform = "translateY(0)";
    }, 200 * (index + 1));
  });
});

window.onload = function () {
  const matchContents = document.querySelectorAll(".match-content");

  matchContents.forEach((match, index) => {
    setTimeout(() => {
      match.style.opacity = 1;
      match.style.transform = "translateY(0)";
    }, index * 100);
  });
};
