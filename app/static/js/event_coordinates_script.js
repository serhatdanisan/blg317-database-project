document.addEventListener("DOMContentLoaded", () => {
  const eventMaps = [
    { containerID: "event-map-1", points: shots, idSuffix: "1" },
    { containerID: "event-map-2", points: passes, idSuffix: "2" },
    { containerID: "event-map-3", points: interceptions, idSuffix: "3" },
    { containerID: "event-map-4", points: offsides, idSuffix: "4" },
    { containerID: "event-map-5", points: duels, idSuffix: "5" },
    { containerID: "event-map-6", points: fouls, idSuffix: "6" },
    { containerID: "event-map-7", points: freekicks, idSuffix: "7" },
    { containerID: "event-map-8", points: saves, idSuffix: "8" },
  ];

  function getFirstTwoDigits(input) {
    if (typeof input === "number") {
      input = input.toString();
    }
    return input.slice(0, 2);
  }

  eventMaps.forEach(({ containerID, points, idSuffix }) => {
    const container = document.getElementById(containerID);
    const field = container.querySelector(".event-map__field");
    const gridChild = document.createElement("div");
    gridChild.classList.add("event-map__grid-child");
    field.appendChild(gridChild);

    if (!container) return;

    const highlightCircle = container.querySelector(
      `#event-map__highlight-circle-${idSuffix}`
    );
    const dynamicLine = container.querySelector(
      `#event-map__dynamic-line-${idSuffix}`
    );
    const circles = container.querySelectorAll(".event-map__circle");

    const infoBox = document.createElement("div");
    infoBox.classList.add("info-box");
    field.appendChild(infoBox);

    function updateInfoBoxContent(point) {
      const content = [];
      const baseUrl = document.getElementById("base-url").dataset.url;
        content.push(`
        <div class="club-logo-row">
          <span class="minute">${point.minute || "N/A"}'</span>
          ${
            point.club_id
              ? `<img class="club-logo" src="/static/images/Clubs/${point.club_id}.png" alt="Club Logo">`
              : ""
          }
        </div>
      `);

      content.push(`
        <div class="first-row">
          ${
            point.player_id
              ? `<img class="player-image" src="${
                  playerImages[point.player_id]
                }" alt="Player Image">`
              : ""
          }
          
          <span class="player-name">
<a href="${baseUrl.replace('0', point.player_id)}">${point.player_name}</a>
          </span>
        </div>
      `);
      if (point.result) {
        content.push(`
          <div class="goal-position">
          <div class="goal-svg">
            <svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="-15 -10 120 40">
            <g>
                <path fill="#414141"
                      d="M503.369 407.8l11.792-4.027-.322-.946-11.553 3.944V402.4h.138l11.833-7.071-.514-.858-11.595 6.929h-12.556l4.87-6.087-.781-.625-5.11 6.388v.324h-11.714v-.035l2.951-6.149-.9-.432-3.049 6.353v.263h-11.716v-.149l-3.049-6.467-.9.432 2.951 6.149v.035h-11.716v-.324l-5.11-6.388-.781.625 4.87 6.087h-11.573l-.121-.062v-.087h-.17l-11.316-5.8-.456.89 10.942 5.6v4.481l-10.552-3.6-.324.946 10.876 3.714v4.441l-10.59-2.712-.248.969 10.838 2.775v4.548l-11.13-1.9-.168.986 11.3 1.922V424h1v-5.4h11.715v5.4h1v-5.4h11.714v5.4h1v-5.4h11.714v5.4h1v-5.4h11.714v5.4h1v-5.406h11.715V424h1v-5.478l11.3-1.929-.168-.986-11.13 1.907V413.2h.064l11.774-3.015-.248-.969-11.59 2.968V407.8zm-1.083-1h-11.715v-4.4h11.715zm-12.715-4.4v4.4h-11.714v-4.4zm-24.428 5.384l11.714.005v4.411h-11.714zm-1 4.416h-11.714v-4.422h11.714zm13.714-4.411l11.714.005v4.406h-11.714zm-1-5.389v4.4h-11.714v-4.4zm-12.714 0v4.4h-11.714v-4.4zm-24.429 0h11.715v4.4H439.8l-.083-.029zm0 5.373l11.715.005v4.422h-11.652l-.063-.016zm0 9.834v-4.422h11.715v4.418zm12.715 0v-4.418h11.714v4.414zm12.714 0v-4.413h11.714v4.406zm12.714 0v-4.409h11.714v4.4zm24.429 0h-11.715v-4.4h11.715zm0-5.4h-11.715v-4.406l11.715.005z"
                      transform="translate(-426 -394)">
                </path>
                <path fill="#E5E5E5" stroke="#E5E5E5" stroke-width="0.5" stroke-linejoin="round" stroke-linecap="round"
                      d="M428 424v-27a1 1 0 0 1 1-1h84a1 1 0 0 1 1 1v27h2v-27a3 3 0 0 0-3-3h-84a3 3 0 0 0-3 3v27z"
                      transform="translate(-426 -394)">
                </path>
            </g>
        </svg>
        </div>
            <div class="event-map__grid-child" 
                 style="grid-area: ${point.modifier || "auto"}; 
                        display: ${
                          point.end_y_coordinate !== -1 ? "block" : "none"
                        };">
            </div>
          </div>
                `);
      }
      // Remaining Rows
      if (point.action) {
        content.push(
          `<div class="content-row"><strong>Action:</strong> <p>${point.action}</p></div>`
        );
      }
      if (!point.result && point.modifier) {
        content.push(
          `<div class="content-row"><strong>Modifier:</strong> <p>${point.modifier}</p></div>`
        );
      }
      if (point.distance) {
        content.push(
          `<div class="content-row"><strong>Distance:</strong> <p>${point.distance} m</p></div>`
        );
      }
      if (point.result) {
        content.push(
          `<div class="content-row"><strong>Result:</strong> <p>${point.result}</p></div>`
        );
      }
      if (point.situation && point.situation !== "") {
        content.push(
          `<div class="content-row"><strong>Situation:</strong> <p>${point.situation}</p></div>`
        );
      }

      infoBox.innerHTML = content.join("");
    }

    function setInfoBoxPosition(point) {
      const xMid = 105 / 2;
      const yMid = 68 / 2;

      let boxX, boxY;

      if (point.x_coordinate < xMid) {
        boxX = (3 / 4) * 105;
      } else {
        boxX = (1 / 4) * 105;
      }
      infoBox.style.left = `${boxX}%`;
      infoBox.style.top = `50%`;
      infoBox.style.transform = "translate(-50%, -50%)";
    }

    const selectAllHomeCheckbox = container.querySelector(
      `#select-all-home-checkbox-${idSuffix}`
    );
    const homePlayerCheckboxes = container.querySelectorAll(
      `.home-players .player-select[id$="-${idSuffix}"]`
    );

    const selectAllAwayCheckbox = container.querySelector(
      `#select-all-away-checkbox-${idSuffix}`
    );
    const awayPlayerCheckboxes = container.querySelectorAll(
      `.away-players .player-select[id$="-${idSuffix}"]`
    );

    let currentPointIndex = null;

    let start = 0;
    let end = 90;

    function updatePointDetails(index) {
      const point = points[index];
      highlightCircle.style.display = "block";
      highlightCircle.setAttribute("cx", point.x_coordinate);
      highlightCircle.setAttribute("cy", point.y_coordinate);

      const circleRadius = parseFloat(highlightCircle.getAttribute("r")) || 3;

      if (point.end_x_coordinate !== -1 && point.end_y_coordinate !== -1) {
        const dx = point.end_x_coordinate - point.x_coordinate;
        const dy = point.end_y_coordinate - point.y_coordinate;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
          const offsetX = (dx / distance) * circleRadius;
          const offsetY = (dy / distance) * circleRadius;
          dynamicLine.style.display = "block";
          dynamicLine.setAttribute("x1", point.x_coordinate + offsetX);
          dynamicLine.setAttribute("y1", point.y_coordinate + offsetY);
          dynamicLine.setAttribute("x2", point.end_x_coordinate);
          dynamicLine.setAttribute("y2", point.end_y_coordinate);
        }
      } else {
        dynamicLine.style.display = "none";
      }

      updateInfoBoxContent(point);
    }

    function updateVisibleShots(startVal, endVal) {
      const allCheckboxes = [...homePlayerCheckboxes, ...awayPlayerCheckboxes];
      const selectedPlayerIds = new Set();

      allCheckboxes.forEach((checkbox) => {
        if (checkbox.checked) {
          const parts = checkbox.id.split("-");

          const playerId = parseInt(parts[parts.length - 2], 10);
          selectedPlayerIds.add(playerId);
        }
      });

      points.forEach((point, index) => {
        const pointMinute = parseInt(getFirstTwoDigits(point.minute), 10);
        const withinRange = pointMinute >= startVal && pointMinute <= endVal;
        const circle = circles[index];

        if (
          withinRange &&
          selectedPlayerIds.has(point.player_id) &&
          !(point.x_coordinate == -1 && point.y_coordinate == -1)
        ) {
          circle.style.display = "block";
        } else {
          circle.style.display = "none";

          if (currentPointIndex === index) {
            highlightCircle.style.display = "none";
            dynamicLine.style.display = "none";
          }
        }
      });
    }

    document.addEventListener("sliderChange", (e) => {
      if (e.detail.containerID === containerID) {
        start = e.detail.startValue;
        end = e.detail.endValue;
        updateVisibleShots(start, end);
      }
    });

    selectAllHomeCheckbox.addEventListener("change", () => {
      const isChecked = selectAllHomeCheckbox.checked;
      homePlayerCheckboxes.forEach((cb) => (cb.checked = isChecked));
      updateVisibleShots(start, end);
    });

    selectAllAwayCheckbox.addEventListener("change", () => {
      const isChecked = selectAllAwayCheckbox.checked;
      awayPlayerCheckboxes.forEach((cb) => (cb.checked = isChecked));
      updateVisibleShots(start, end);
    });

    function allChecked(checkboxes) {
      return Array.from(checkboxes).every((cb) => cb.checked);
    }

    homePlayerCheckboxes.forEach((cb) => {
      cb.addEventListener("change", () => {
        selectAllHomeCheckbox.checked = allChecked(homePlayerCheckboxes);
        updateVisibleShots(start, end);
      });
    });

    awayPlayerCheckboxes.forEach((cb) => {
      cb.addEventListener("change", () => {
        selectAllAwayCheckbox.checked = allChecked(awayPlayerCheckboxes);
        updateVisibleShots(start, end);
      });
    });

    circles.forEach((circle, index) => {
      circle.addEventListener("click", (event) => {
        event.stopPropagation();

        if (
          currentPointIndex === index &&
          highlightCircle.style.display === "block"
        ) {
          highlightCircle.style.display = "none";
          dynamicLine.style.display = "none";
          infoBox.style.visibility = "hidden";
          circle.classList.remove("active");
          currentPointIndex = null;

          updateVisibleShots(start, end);
        } else {
          currentPointIndex = index;

          circles.forEach((c, i) => {
            if (i !== index) {
              c.style.display = "none";
            }
          });

          circle.classList.add("active");
          updatePointDetails(index);
          updateInfoBoxContent(points[index]);
          setInfoBoxPosition(points[index]);

          infoBox.style.visibility = "visible";
        }
      });
    });
    field.addEventListener("click", (event) => {
      const isClickInsideInfoBox = infoBox.contains(event.target);

      if (!isClickInsideInfoBox && currentPointIndex !== null) {
        updateVisibleShots(start, end);
        infoBox.style.visibility = "hidden";
        highlightCircle.style.display = "none";
        dynamicLine.style.display = "none";
        circles[currentPointIndex].classList.remove("active");
        currentPointIndex = null;
      }
    });
    updateVisibleShots(start, end);
  });
});
