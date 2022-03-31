const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function expressMiddleware(router) {
    router.use(
        "/media",
        createProxyMiddleware({
            target: "http://localhost:8090",
            changeOrigin: true,
        })
    );
};
