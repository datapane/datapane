import "./src/styles/base.scss";
import "./src/styles/templates-base.scss";
import "./src/styles/tailwind.css"; // This import is skipped in production; see `base/vite.config.ts`

// JS Polyfills
import "whatwg-fetch";
import "./src/polyfills";

import "htmx.org/dist/htmx";
import { setupPostHog } from "../shared/dp-track";
import { DPClipboard } from "../shared/DPClipboard";

// Window objects
window.errorHandler = window.errorHandler || {};

export { setupPostHog, DPClipboard };
