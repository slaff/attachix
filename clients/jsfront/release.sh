./js apps/front/compress.js
java -jar tools/yuicompressor-2.4.7.jar apps/front/production.js -o apps/front/production.js
(cd resources/ace; ./release.sh)
