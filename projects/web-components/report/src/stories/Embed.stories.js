import Embed from "../components/blocks/Embed.vue";
import { makeTemplate } from "./utils";

export default {
    title: "Embed",
    component: Embed,
};

export const Primary = makeTemplate(Embed);

Primary.args = {
    html:
        // eslint-disable-next-line quotes
        '<iframe width="720" height="540" src="https://www.youtube.com/embed/JDe14ulcfLA?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="" title="Datapane Quick Overview"></iframe>',
    isIframe: true,
};
