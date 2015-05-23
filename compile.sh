# compile scss -> css
# and minify css
sass ./static/scss/primer.scss ./static/css/primer.css --style compressed
# compile coffee -> js
# and minify js
coffee --compile --output static/js static/coffee
