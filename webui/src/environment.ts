/* global process:true */

const getHostName = (): string | null => {
    return window.dpLocal ? null : window.location.origin.concat("/");
};

const env: any = {};
env.url = getHostName();
export default env;
