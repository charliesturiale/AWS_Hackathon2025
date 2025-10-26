const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Exclude heavy directories from watching
config.watchFolders = [__dirname];
config.resolver.blacklistRE = /(.git|.cache|.expo|node_modules\/.*\/node_modules).*$/;
config.resolver.blockList = [
  /node_modules\/.*\/node_modules\/.*/,
  /.git\/.*/,
  /.expo\/.*/,
];

// Reduce the number of workers
config.maxWorkers = 2;

module.exports = config;