# compile scss -> css
# and minify css
sass ./static/scss/internal.scss ./static/css/internal.min.css --style compressed --sourcemap=none
# compile coffee -> js
coffee --compile --output static/js static/coffee
# and minify js
# uglifyjs static/js/loader.js -o foo.min.js -c -m
