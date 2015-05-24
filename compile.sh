# compile scss -> css
# and minify css
sass ./static/scss/primer.scss ./static/css/primer.css --style compressed
# compile coffee -> js
coffee --compile --output static/js static/coffee
# and minify js
# uglifyjs static/js/loader.js -o foo.min.js -c -m
