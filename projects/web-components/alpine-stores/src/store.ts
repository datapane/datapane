/**
 * Global Alpine stores
 */

import notebookjs from "./dp-notebook/dpNotebook";
import { EventType } from "../../shared/types";

/* reportSource constants */
const DRAG_BORDER_HEIGHT = 8; // height of the draggable area around the top of the element
const DRAG_MIN_HEIGHT = 30; // min height of the draggable element

const disableSelect = (event: any) => {
    event.preventDefault();
};

window.addEventListener("alpine:init", () => {
    const { Alpine } = window;

    Alpine.store("copy", {
        show: false,
        toggle() {
            this.show = true;
            setTimeout(() => (this.show = false), 2000);
        },
    });

    Alpine.store("schedule", {
        disableSave: false,
        init() {
            window.addEventListener(EventType.SCHEDULE_DISABLED, (evt: any) => {
                this.disableSave = evt.detail;
            });
        },
    });

    Alpine.store("reportSource", {
        on: false,
        rendered: false,
        sourceFileUrl: undefined,
        dragPos: 0,
        resizeListener: undefined,
        async render() {
            try {
                const res = await fetch(this.sourceFileUrl);
                const json = await res.json();

                const notebook = (notebookjs as any).parse(json);
                const target = document.querySelector("#ipynb-target");

                if (!target) {
                    throw "Couldn't find ipynb target element";
                }

                target.innerHTML = ""; // Clear loading spinner, if any
                target.appendChild(notebook.render());
                this.rendered = true;
            } catch (e) {
                console.error("Report ipynb source error", e);
            }
        },
        toggle() {
            if (!this.rendered && !this.on) {
                this.render();
            }
            this.on = !this.on;
        },
        dragStart(el: HTMLElement, event: any) {
            if (event.offsetY < DRAG_BORDER_HEIGHT) {
                this.dragPos = event.y;
                this.resizeListener = (e: MouseEvent) => this.resize(el, e);

                // Resize el on mousemove while dragging
                document.addEventListener(
                    "mousemove",
                    this.resizeListener,
                    false
                );

                // Disable text/image highlighting while dragging
                document.addEventListener("selectstart", disableSelect);
            }
        },
        dragEnd() {
            document.removeEventListener(
                "mousemove",
                this.resizeListener,
                false
            );
            document.removeEventListener("selectstart", disableSelect);
        },
        resize(el: HTMLElement, event: any) {
            const dy = this.dragPos - event.y;
            this.dragPos = event.y;

            const screenHeight =
                window.innerHeight ||
                document.documentElement.clientHeight ||
                document.body.clientHeight;
            if (
                this.dragPos < 0 ||
                this.dragPos > screenHeight - DRAG_MIN_HEIGHT
            ) {
                // If the user drags outside the window then end the drag
                this.dragEnd();
            } else {
                el.style.height = `${
                    parseInt(getComputedStyle(el).height) + dy
                }px`;
            }
        },
    });
});
