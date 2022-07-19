import "./src/styles/notebook.scss";
import "./src/styles/base.scss";
import "./src/styles/tailwind.css";
import "./src/styles/templates-base.scss";

// JS Polyfills
import "whatwg-fetch";
import "./src/polyfills";

import "htmx.org/dist/htmx";
import { setupPostHog } from "../shared/dp-track";
import { DPClipboard } from "../shared/DPClipboard";

// Window objects
window.errorHandler = window.errorHandler || {};

export { setupPostHog, DPClipboard };
