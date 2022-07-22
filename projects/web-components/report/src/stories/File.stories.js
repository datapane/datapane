import File from "../components/blocks/File.vue";
import { makeTemplate } from "./utils";

export default {
    title: "File",
    component: File,
};

export const Primary = makeTemplate(File);

Primary.args = {
    filename: "foo.tar",
    downloadFile: () => Promise.resolve(),
};
