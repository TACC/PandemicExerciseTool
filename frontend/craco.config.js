module.exports = {
    webpack: {
      configure: (webpackConfig) => {
        const oneOfRule = webpackConfig.module.rules.find(rule => rule.oneOf);
        const cssRule = oneOfRule.oneOf.find(rule => rule.test && rule.test.toString().includes('css'));
        cssRule.include = undefined;
        cssRule.exclude = /\.module\.css$/;
        return webpackConfig;
      }
    }
  };
  