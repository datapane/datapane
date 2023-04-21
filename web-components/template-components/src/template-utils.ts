type VisibilityOptions = {
    initialOpen?: boolean;
    callback?: (isVisible: boolean) => void;
};

export const onLoad = (f: EventListenerOrEventListenerObject) =>
    window.addEventListener("DOMContentLoaded", f);

export const toggleVisibility = (
    elementSelector: string,
    toggleVisibilitySelectors: string[],
    options: VisibilityOptions = {},
) =>
    /**
     * Toggle visibility of element with callback
     * elementSelector: The element whose visibility should be toggled
     * toggleVisibilitySelectors: A list of element selectors that toggle the visibility of the element when clicked
     */
    onLoad(() => {
        const elementToToggle = document.querySelector(elementSelector);

        if (!elementToToggle) {
            throw new Error(`Can't find element to toggle: ${elementSelector}`);
        }

        if (options.initialOpen) {
            elementToToggle.classList.remove("dp-invisible");
        }

        for (const selector of toggleVisibilitySelectors) {
            const clickToggleElement = document.querySelector(selector);

            if (!clickToggleElement) {
                throw new Error(`Can't find clickable element: ${selector}`);
            }

            clickToggleElement.addEventListener("click", () => {
                elementToToggle.classList.toggle("dp-invisible");
                if (options.callback) {
                    options.callback(
                        !elementToToggle.classList.contains("dp-invisible"),
                    );
                }
            });
        }
    });

export const serializeSlotJson = <T = Record<any, any>>(
    slot: HTMLSlotElement,
): T => {
    /**
     * Fetch and serialize JSON script inside web component slot. Used for passing
     * JSON data into web components while keeping the scope of the JSON object within the web component
     */
    try {
        const slotContent = slot.assignedNodes()[0] as Element;
        return JSON.parse(
            slotContent.querySelector("script[type='application/json']")
                .textContent,
        );
    } catch (e) {
        throw new Error(`Couldn't serialize slot content: ${e}`);
    }
};
