document.addEventListener("DOMContentLoaded", () => {
  let currentShotIndex = 0;

  const highlightCircle = document.getElementById("highlight-circle");
  const shotMinute = document.getElementById("shot-minute");
  const playerName = document.getElementById("shot-player-name");
  const shotResult = document.getElementById("shot-result");
  const shotSituation = document.getElementById("shot-situation");

  const prevButton = document.getElementById("prev-shot");
  const nextButton = document.getElementById("next-shot");

  const circles = document.querySelectorAll(".shot-circle");

  function updateShotDetails(index) {
    const shot = shots[index];

    highlightCircle.style.display = "block";
    highlightCircle.setAttribute("cx", shot.x_coordinate);
    highlightCircle.setAttribute("cy", shot.y_coordinate);

    shotMinute.textContent = `${shot.minute}'`;
    playerName.textContent = `${shot.player_name}`;
    shotResult.textContent = `${shot.result}`;
    shotSituation.textContent = `${shot.situation}`;

    circles.forEach((circle) => circle.classList.remove("active"));

    const activeCircle = circles[index];
    activeCircle.classList.add("active");
  }

  function changeShot(direction) {
    if (direction === "next") {
      currentShotIndex = (currentShotIndex + 1) % shots.length;
    } else if (direction === "prev") {
      currentShotIndex = (currentShotIndex - 1 + shots.length) % shots.length;
    }
    updateShotDetails(currentShotIndex);
  }

  circles.forEach((circle, index) => {
    circle.addEventListener("click", () => {
      currentShotIndex = index;
      updateShotDetails(currentShotIndex);
    });
  });

  updateShotDetails(currentShotIndex);

  prevButton.addEventListener("click", () => changeShot("prev"));
  nextButton.addEventListener("click", () => changeShot("next"));
});
