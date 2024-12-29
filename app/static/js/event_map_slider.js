document.addEventListener("DOMContentLoaded", function () {

    const eventMaps = [
        { containerID: "event-map-1", idSuffix: "1" },
        { containerID: "event-map-2", idSuffix: "2" },
        { containerID: "event-map-3", idSuffix: "3" },
        { containerID: "event-map-4", idSuffix: "4" },
        { containerID: "event-map-5", idSuffix: "5" },
        { containerID: "event-map-6", idSuffix: "6" },
        { containerID: "event-map-7", idSuffix: "7" },
        { containerID: "event-map-8", idSuffix: "8" },
    ];

    eventMaps.forEach(({ containerID, idSuffix }) => {
        const container = document.getElementById(containerID);
        if (!container) {
            console.warn(`[${idSuffix}] Container with ID "${containerID}" not found.`);
            return;
        }

        const sliderContainer = container.querySelector(".double-slider-container");
        if (!sliderContainer) {
            console.warn(`[${idSuffix}] .double-slider-container not found in "${containerID}".`);
            return;
        }

        const thumbStart = document.getElementById(`thumb-start-${idSuffix}`);
        const thumbEnd = document.getElementById(`thumb-end-${idSuffix}`);
        const sliderRange = sliderContainer.querySelector(".slider-range");
        const labelStart = document.getElementById(`label-start-${idSuffix}`);
        const labelEnd = document.getElementById(`label-end-${idSuffix}`);

        if (!thumbStart || !thumbEnd || !sliderRange || !labelStart || !labelEnd) {
            console.warn(`[${idSuffix}] One or more slider elements not found in "${containerID}".`);
            return;
        }

        const setFirstHalfButton = document.getElementById(`set-first-half-${idSuffix}`);
        const setSecondHalfButton = document.getElementById(`set-second-half-${idSuffix}`);
        const setFullMatchButton = document.getElementById(`set-full-match-${idSuffix}`);

        const minValue = 0;
        const maxValue = 90;
        let startPercent = 0;
        let endPercent = 100;

        const thumbWidth = thumbStart.offsetWidth;

        let activeThumb = null;

        function percentToValue(pct) {
            const val = Math.round((pct / 100) * (maxValue - minValue) + minValue);
            return val;
        }

        function valueToPercent(value) {
            const pct = ((value - minValue) / (maxValue - minValue)) * 100;
            return pct;
        }

        function updatePositions() {

            thumbStart.style.left = `${startPercent}%`;
            thumbEnd.style.left = `${endPercent}%`;

            sliderRange.style.left = `${startPercent}%`;
            sliderRange.style.width = `${endPercent - startPercent}%`;

            const startValue = percentToValue(startPercent);
            const endValue = percentToValue(endPercent);

            labelStart.textContent = startValue;
            labelEnd.textContent = endValue;

            updateTickVisibility(startPercent, endPercent);

            const sliderChangeEvent = new CustomEvent("sliderChange", {
                detail: {
                    containerID: containerID, 
                    startValue: startValue,
                    endValue: endValue,
                },
            });
            document.dispatchEvent(sliderChangeEvent);

        }

        function showLabelTemporarily(label) {
            label.style.display = "block";
            setTimeout(() => {
                label.style.display = "none";
            }, 200);
        }

        sliderContainer.addEventListener("click", (e) => {

            if (e.target === sliderContainer || e.target.classList.contains("slider-range")) {
                const sliderRect = sliderContainer.getBoundingClientRect();
                const sliderWidth = sliderContainer.offsetWidth - thumbWidth;

                const clickX = e.clientX - sliderRect.left;
                const clickPercent = (clickX / sliderWidth) * 100;

                const startDistance = Math.abs(clickPercent - startPercent);
                const endDistance = Math.abs(clickPercent - endPercent);

                const minGapPercent = 100 / (maxValue - minValue + 1);

                if (startDistance < endDistance) {

                    const newStart = Math.max(
                        0,
                        Math.min(clickPercent, endPercent - minGapPercent)
                    );
                    startPercent = newStart;
                    updatePositions();
                    showLabelTemporarily(labelStart);
                } else {

                    const newEnd = Math.min(
                        100,
                        Math.max(clickPercent, startPercent + minGapPercent)
                    );
                    endPercent = newEnd;
                    updatePositions();
                    showLabelTemporarily(labelEnd);
                }
            }
        });

        thumbStart.addEventListener("mousedown", (e) => onMouseDown(e, true));
        thumbEnd.addEventListener("mousedown", (e) => onMouseDown(e, false));

        function onMouseMove(e) {
            if (!activeThumb) return;

            const sliderRect = sliderContainer.getBoundingClientRect();
            const sliderW = sliderContainer.offsetWidth - thumbWidth;
            let newLeft = e.clientX - sliderRect.left;

            let newPercent = (newLeft / sliderW) * 100;

            const step = 1;
            const stepPercent = (step / (maxValue - minValue)) * 100;

            newPercent = Math.round(newPercent / stepPercent) * stepPercent;

            if (activeThumb === thumbStart) {

                newPercent = Math.max(0, Math.min(newPercent, endPercent - stepPercent));
                startPercent = newPercent;
            } else if (activeThumb === thumbEnd) {

                newPercent = Math.min(100, Math.max(newPercent, startPercent + stepPercent));
                endPercent = newPercent;
            }

            updatePositions();
        }

        function onMouseUp() {
            document.removeEventListener("mousemove", onMouseMove);
            document.removeEventListener("mouseup", onMouseUp);

            labelStart.style.display = "none";
            labelEnd.style.display = "none";

            activeThumb = null;
        }

        function onMouseDown(e, isStart) {
            activeThumb = isStart ? thumbStart : thumbEnd;

            if (isStart) {
                labelStart.style.display = "block";
                labelEnd.style.display = "none";
            } else {
                labelEnd.style.display = "block";
                labelStart.style.display = "none";
            }

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);

            e.preventDefault();
        }

        function updateTickVisibility(sp, ep) {
            const ticks = sliderContainer.querySelectorAll(".slider-ticks .tick");
            ticks.forEach((tick) => {
                const tickPercent = parseFloat(tick.style.left);

                if (tickPercent < sp || tickPercent > ep) {
                    tick.style.display = "none";
                } else {
                    tick.style.display = "block";
                }
            });
        }

        setSecondHalfButton.addEventListener("click", () => {
            startPercent = valueToPercent(46); 
            endPercent = valueToPercent(90);   
            updatePositions();
        });

        setFirstHalfButton.addEventListener("click", () => {
            startPercent = valueToPercent(0);  
            endPercent = valueToPercent(45);   
            updatePositions();
        });

        setFullMatchButton.addEventListener("click", () => {
            startPercent = valueToPercent(0);  
            endPercent = valueToPercent(90);   
            updatePositions();
        });

        labelStart.style.display = "none";
        labelEnd.style.display = "none";

        updatePositions();
    });

});