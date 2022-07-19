/**
 * Sets remaining CSS theme vars based on existing vars set by Tailwind config,
 * and the light prose setting
 */

import chroma from "chroma-js";

const getCssVar = (name: string): string => {
    /**
     * Get a global CSS variable by name
     */
    const varName = getComputedStyle(document.body).getPropertyValue(name);
    return varName.trim().replace(/["']/g, "");
};

export const setTheme = (isLightProse?: boolean) => {
    /**
     * Set the global report theme based on global CSS vars,
     * and set text brightness based on `isLightProse`
     */
    const lightFontColor = isLightProse
        ? "rgb(209, 213, 219)"
        : "rgb(107, 114, 128)"; /* gray-300 : gray-500 */
    const darkFontColor = isLightProse
        ? "rgb(107, 114, 128)"
        : "rgb(55, 65, 81)"; /* gray-500 : gray-700 */

    const accentColor = getCssVar("--dp-accent-color");
    const root = document.documentElement;

    try {
        const color = chroma(accentColor);
        root.style.setProperty(
            "--dp-accent-secondary-color",
            color.alpha(0.14).hex()
        );
        root.style.setProperty(
            "--dp-accent-text",
            color.get("lab.l") < 70 ? "white" : "black"
        );
        root.style.setProperty("--dp-light-gray", lightFontColor);
        root.style.setProperty("--dp-dark-gray", darkFontColor);
    } catch (e) {
        console.error("An error occurred while setting a theme property: ", e);
    }
};
