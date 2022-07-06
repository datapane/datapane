const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function expressMiddleware(router) {
    /**
     * Proxy `/media` calls in storybook server to dp server
     */
    router.use(
        "/media",
        createProxyMiddleware({
            target: "http://localhost:8090",
            changeOrigin: true,
        })
    );
};
