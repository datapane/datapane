import "./src/styles/base.scss";
import "./src/styles/templates-base.scss";
import "./src/styles/tailwind.css";
import { setupPostHog } from "../shared/dp-track";
import { DPClipboard } from "../shared/DPClipboard";

// JS Polyfills
import "whatwg-fetch";
import "./src/polyfills";

import "htmx.org/dist/htmx";

// Window objects
window.errorHandler = window.errorHandler || {};

export { setupPostHog, DPClipboard };
