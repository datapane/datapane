import Folium from "../components/blocks/Folium.vue";
import { makeTemplate } from "./utils";
import iframeContent from "./assets/folium.html?raw";

export default {
    title: "Folium",
    component: Folium,
};

export const Primary = makeTemplate(Folium);

Primary.args = {
    singleBlockEmbed: false,
    iframeContent,
};
