import { createApp } from "vue";
import { plugin as formkitPlugin, defaultConfig } from "@formkit/vue";
import Observer from "mobx-vue-lite";
import Params from "./src/components/Params.vue";
import "@formkit/themes/genesis";
import { paramsStore } from "./src/data-model/params-store";

const mountParams = (props: any) => {
    const app = createApp(Params, props);
    app.use(formkitPlugin, defaultConfig);
    app.use(Observer);
    app.mount("#params");
    return app;
};

window.$testResources = { paramsStore };

export { mountParams };
