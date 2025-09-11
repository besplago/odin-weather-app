const { merge } = require("webpack-merge");
const common = require("./webpack.common.js");

module.exports = merge(common, {
  mode: "development",
  devtool: "eval-source-map",
  devServer: {
    static: "./dist",
    watchFiles: ["./src/template.html"],
    client: {
      overlay: true,
    },
  },
  watchOptions: {
    poll: 1000,
    ignored: ["**/node_modules"],
  },
});
