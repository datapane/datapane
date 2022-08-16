import notebookjs from "./notebook";
import hljs from "highlight.js/lib/core";
import "highlight.js/styles/docco.css";
import python from "highlight.js/lib/languages/python";
import json from "highlight.js/lib/languages/json";
import markdown from "highlight.js/lib/languages/markdown";

const HLJS_LANGS: any = {
    python,
    json,
    markdown,
};

Object.keys(HLJS_LANGS).forEach((l) => hljs.registerLanguage(l, HLJS_LANGS[l]));

const highlighter = (code: string, lang: string) => {
    if (typeof lang === "undefined") lang = "markup";

    if (Object.keys(HLJS_LANGS).includes(lang)) {
        try {
            return hljs.highlight(code, { language: lang }).value;
        } catch (e) {
            console.warn(`Failed to use hljs language: ${lang}`);
            return code;
        }
    } else {
        return code;
    }
};

(notebookjs as any).highlighter = function (
    text: string,
    pre: HTMLPreElement,
    code: HTMLElement,
    lang: string
) {
    const language = lang || "python";
    pre.className = "language-" + language;
    if (typeof code != "undefined") {
        code.className = "language-" + language;
    }
    return highlighter(text, language);
};

export default notebookjs;
