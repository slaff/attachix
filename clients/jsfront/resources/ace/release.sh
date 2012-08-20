ls *.js| grep -v production.js | grep -v 'worker-' | xargs cat > production.js
java -jar ../../tools/yuicompressor-2.4.7.jar production.js -o production.js
